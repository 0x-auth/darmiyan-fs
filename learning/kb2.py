"""
Follow-up: is the failure of "KB as input" a capacity problem?
KB sizes 8, 16, 32 chains (16, 32, 64 facts) against a 16-fact window.
Input taught two ways:
  A  one-step questions only                 -> test never-asked two-step
  B  one-step all + two-step on half chains  -> test two-step on the other half
Same frozen model as kb_input.py (identical seeds; cached in frozen.pt).
"""
import os, copy, torch, torch.nn as nn, torch.nn.functional as F
import kb_input as K

def get_model():
    m = K.Model()
    if os.path.exists("frozen.pt"):
        m.load_state_dict(torch.load("frozen.pt"))
    else:
        K.pretrain(m, 14000); torch.save(m.state_dict(), "frozen.pt")
    m.eval()
    for p in m.parameters(): p.requires_grad_(False)
    return m

def evaluate(model, KC, seed=2026):
    kb = K.chains(KC, torch.Generator().manual_seed(seed))
    facts = torch.cat([kb[:, :2], kb[:, 1:]])
    one = [(kb[j, 0], K.HOP1, kb[j, 1]) for j in range(KC)] + [(kb[j, 1], K.HOP1, kb[j, 2]) for j in range(KC)]
    two = [(kb[j, 0], K.HOP2, kb[j, 2]) for j in range(KC)]
    half = KC // 2
    ans = lambda qs: torch.tensor([a for *_, a in qs])
    out = {}

    def rag(q, h, extra=()):
        keys = {int(q), *map(int, extra)}
        hit = [f for f in facts if int(f[0]) in keys or int(f[1]) in keys]
        g = torch.Generator().manual_seed(int(q) + 5)
        rest = [f for f in facts[torch.randperm(len(facts), generator=g)] if not any((f == x).all() for x in hit)]
        return K.context_ids(torch.stack((hit + rest)[:K.NF]), q, h)
    with torch.no_grad():
        p = model(torch.stack([rag(q, h) for q, h, _ in two])).argmax(1)
        out["RAG one round"] = (p == ans(two)).float().mean().item()
        mid = model(torch.stack([rag(q, K.HOP1) for q, _, _ in two])).argmax(1)
        p = model(torch.stack([rag(q, K.HOP2, (m,)) for (q, _, _), m in zip(two, mid)])).argmax(1)
        out["RAG two rounds"] = (p == ans(two)).float().mean().item()

    def qpart(q, h):
        ids = torch.cat([torch.zeros(2 * K.NF, dtype=torch.long), torch.tensor([q, h])])
        return model.embed(ids.unsqueeze(0))[0, -2:]

    def learn_input(train_qs, steps=3000, lr=3e-2):
        base = model.embed(K.context_ids(facts[:K.NF], 0, K.HOP1).unsqueeze(0))[0, :-2].detach()
        P = nn.Parameter(base.clone())
        opt = torch.optim.Adam([P], lr)
        Q = torch.stack([qpart(q, h) for q, h, _ in train_qs]).detach(); A = ans(train_qs)
        for _ in range(steps):
            x = torch.cat([P.unsqueeze(0).expand(len(Q), -1, -1), Q], 1)
            loss = F.cross_entropy(model.run(x), A); opt.zero_grad(); loss.backward(); opt.step()
        return P.detach()

    def acc_input(P, qs):
        Q = torch.stack([qpart(q, h) for q, h, _ in qs])
        with torch.no_grad():
            return (model.run(torch.cat([P.unsqueeze(0).expand(len(Q), -1, -1), Q], 1)).argmax(1) == ans(qs)).float().mean().item()

    PA = learn_input(one)
    out["input A: taught 1-step"] = acc_input(PA, one)
    out["input A: 2-step (never asked)"] = acc_input(PA, two)
    PB = learn_input(one + two[:half])
    out["input B: 2-step taught half"] = acc_input(PB, two[:half])
    out["input B: 2-step other half"] = acc_input(PB, two[half:])
    return out

if __name__ == "__main__":
    model = get_model()
    a1, a2 = K.in_context_acc(model)
    print(f"frozen model, facts in window: 1-step {a1:.3f}, 2-step {a2:.3f}\n")
    rows = {KC: evaluate(model, KC) for KC in (8, 16, 32)}
    keys = list(rows[8].keys())
    print(f"{'':34}" + "".join(f"{f'{2*KC} facts':>12}" for KC in rows))
    for k in keys:
        print(f"{k:34}" + "".join(f"{rows[KC][k]:>12.3f}" for KC in rows))
    print(f"\nwindow holds {K.NF} facts; chance {1/K.E:.3f}")
