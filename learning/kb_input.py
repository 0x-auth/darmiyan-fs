"""
Can a knowledge base become a "specialised input" to a frozen model?
--------------------------------------------------------------------
Question (Space, 23 Oct 2026): instead of fine-tuning or RAG, turn a personal
knowledge base into a special input, so the frozen model's own reasoning
connects things across the whole history.

1. Pretrain a small model to reason over facts IN ITS CONTEXT:
   context = 8 shuffled cause->effect chains a->b->c (16 facts),
   query   = (entity, hop 1 or 2)  ->  answer the entity 1 or 2 steps on.
   Then FREEZE it.
2. A personal knowledge base (KB) the model has never seen: 32 chains,
   64 facts, 4x larger than the model's window.
3. Teach the KB with ONE-STEP questions only (a->b, b->c). Then ask TWO-STEP
   questions (a->c) that were never asked. Methods:
     oracle context   the right chain is placed in the window (upper bound)
     RAG, one round   window filled with the facts most similar to the question
     RAG, two rounds  ask one step, retrieve again with the answer, ask again
     fine-tune        weights changed on the one-step questions (window empty)
     KB as input      weights frozen; the window's 16 input vectors are
                      optimised on the one-step questions (Space's idea)
Chance = 1/128.
"""
import math, time, sys, torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0); torch.set_num_threads(2)

E, C, D, L, H = 128, 8, 128, 4, 4            # entities, chains in window, width, layers, heads
NF = 2 * C                                    # facts in window
T = 2 * NF + 2                                # ids per example: facts (a,b pairs) + (query, hop)
TP = NF + 2                                   # model positions: one per fact, query, hop
HOP1, HOP2 = E, E + 1
V = E + 2

class Block(nn.Module):
    def __init__(s):
        super().__init__(); s.n1 = nn.LayerNorm(D); s.n2 = nn.LayerNorm(D)
        s.qkv = nn.Linear(D, 3 * D); s.o = nn.Linear(D, D)
        s.m = nn.Sequential(nn.Linear(D, 4 * D), nn.GELU(), nn.Linear(4 * D, D))
    def forward(s, x):
        B, N, _ = x.shape
        q, k, v = s.qkv(s.n1(x)).split(D, 2)
        q, k, v = [t.view(B, N, H, D // H).transpose(1, 2) for t in (q, k, v)]
        a = F.scaled_dot_product_attention(q, k, v).transpose(1, 2).reshape(B, N, D)
        x = x + s.o(a)
        return x + s.m(s.n2(x))

class Model(nn.Module):
    def __init__(s):
        super().__init__()
        s.tok = nn.Embedding(V, D); s.src = nn.Embedding(E, D); s.pos = nn.Embedding(TP, D)
        s.blocks = nn.ModuleList([Block() for _ in range(L)])
        s.norm = nn.LayerNorm(D)
    def embed(s, ids):
        # one position per fact: cause vector + effect vector; then query, hop
        facts = s.src(ids[:, 0:2 * NF:2]) + s.tok(ids[:, 1:2 * NF:2])
        tail = torch.stack([s.src(ids[:, -2]), s.tok(ids[:, -1])], 1)
        return torch.cat([facts, tail], 1) + s.pos(torch.arange(TP))
    def run(s, x):
        for b in s.blocks: x = b(x)
        return s.norm(x[:, -1]) @ s.tok.weight[:E].T   # output tied to entity vectors
    def forward(s, ids):
        return s.run(s.embed(ids))

def chains(n, gen):
    p = torch.randperm(E, generator=gen)[: 3 * n].view(n, 3)
    return p                                   # each row a -> b -> c

def make_batch(B, gen, p_two=0.5):
    ids = torch.empty(B, T, dtype=torch.long); ans = torch.empty(B, dtype=torch.long)
    for i in range(B):
        ch = chains(C, gen)
        facts = torch.cat([ch[:, :2], ch[:, 1:]])           # 2C facts
        facts = facts[torch.randperm(NF, generator=gen)]
        j = torch.randint(C, (1,), generator=gen).item()
        r = torch.rand(1, generator=gen).item()
        if r < p_two: q, h, a = ch[j, 0], HOP2, ch[j, 2]
        elif torch.rand(1, generator=gen).item() < .5: q, h, a = ch[j, 0], HOP1, ch[j, 1]
        else:         q, h, a = ch[j, 1], HOP1, ch[j, 2]
        ids[i] = torch.cat([facts.flatten(), torch.tensor([q, h])]); ans[i] = a
    return ids, ans

def context_ids(facts, q, h):
    f = facts.clone()
    if len(f) < NF:                                         # pad with dummy facts
        g = torch.Generator().manual_seed(int(q) * 7 + int(h))
        extra = torch.randperm(E, generator=g)[: 2 * (NF - len(f))].view(-1, 2)
        f = torch.cat([f, extra])
    f = f[:NF]
    return torch.cat([f.flatten(), torch.tensor([q, h])])

def pretrain(model, steps):
    opt = torch.optim.AdamW(model.parameters(), 1e-3, weight_decay=0.01)
    gen = torch.Generator().manual_seed(1); t0 = time.time(); p_two = 0.0
    for s in range(steps + 1):
        for g in opt.param_groups: g["lr"] = 1e-3 * min(1, s / 300) * (0.5 * (1 + math.cos(math.pi * s / steps)) * 0.9 + 0.1)
        x, y = make_batch(64, gen, p_two)
        loss = F.cross_entropy(model(x), y); opt.zero_grad(); loss.backward(); opt.step()
        if s % 500 == 0:
            a1, a2 = in_context_acc(model)
            if a1 > 0.9 and p_two == 0: p_two = 0.5; print("  -> one-step learned; adding two-step questions", flush=True)
            print(f"  step {s:5d} loss {loss.item():.3f}  in-context acc: 1-step {a1:.3f} 2-step {a2:.3f}  [{time.time()-t0:.0f}s]", flush=True)

@torch.no_grad()
def in_context_acc(model, n=400):
    gen = torch.Generator().manual_seed(99)
    x, y = make_batch(n, gen); p = model(x).argmax(1)
    two = x[:, -1] == HOP2
    return (p[~two] == y[~two]).float().mean().item(), (p[two] == y[two]).float().mean().item()

def main(steps=int(sys.argv[1]) if len(sys.argv) > 1 else 14000):
    model = Model()
    print(f"pretraining ({sum(p.numel() for p in model.parameters()):,} params)")
    pretrain(model, steps)
    model.eval()
    for p in model.parameters(): p.requires_grad_(False)
    frozen = {k: v.clone() for k, v in model.state_dict().items()}

    # ---- the personal knowledge base: 32 chains, 64 facts (4x the window)
    KC = 32
    kb = chains(KC, torch.Generator().manual_seed(2026))
    facts = torch.cat([kb[:, :2], kb[:, 1:]])
    one_q = [(kb[j, 0], HOP1, kb[j, 1]) for j in range(KC)] + [(kb[j, 1], HOP1, kb[j, 2]) for j in range(KC)]
    two_q = [(kb[j, 0], HOP2, kb[j, 2]) for j in range(KC)]
    print(f"\nKB: {KC} chains, {len(facts)} facts; window holds {NF}. Taught: {len(one_q)} one-step questions. Tested: {len(two_q)} two-step questions never asked.\n")
    res = {}

    @torch.no_grad()
    def ask(ids_list):
        return model(torch.stack(ids_list)).argmax(1)

    # oracle: right chain + random other KB facts
    def oracle(q, h):
        j = (kb == q).nonzero()[0, 0]
        rel = torch.stack([kb[j, :2], kb[j, 1:]])
        others = facts[torch.randperm(len(facts), generator=torch.Generator().manual_seed(int(q)))]
        others = torch.stack([f for f in others if not any((f == r).all() for r in rel)])[: NF - 2]
        return context_ids(torch.cat([rel, others]), q, h)
    # RAG: facts sharing an entity with the query first, then the rest by random "similarity"
    def rag(q, h, extra=()):
        keys = {int(q), *map(int, extra)}
        hit = [f for f in facts if int(f[0]) in keys or int(f[1]) in keys]
        rest = [f for f in facts[torch.randperm(len(facts), generator=torch.Generator().manual_seed(int(q) + 5))] if not any((f == g).all() for g in hit)]
        return context_ids(torch.stack((hit + rest)[:NF]), q, h)

    for name, build in (("oracle context", oracle), ("RAG, one round", rag)):
        p1 = ask([build(q, h) for q, h, _ in one_q]); a1 = torch.tensor([a for *_, a in one_q])
        p2 = ask([build(q, h) for q, h, _ in two_q]); a2 = torch.tensor([a for *_, a in two_q])
        res[name] = ((p1 == a1).float().mean().item(), (p2 == a2).float().mean().item())
    # RAG two rounds: ask one step, retrieve with the answer, ask two steps
    mid = ask([rag(q, HOP1) for q, _, _ in two_q])
    p2 = ask([rag(q, HOP2, extra=(m,)) for (q, _, _), m in zip(two_q, mid)])
    res["RAG, two rounds"] = (res["RAG, one round"][0], (p2 == torch.tensor([a for *_, a in two_q])).float().mean().item())

    # learned input: frozen weights, optimise the window's input vectors
    def query_part(q, h):
        ids = torch.cat([torch.zeros(2 * NF, dtype=torch.long), torch.tensor([q, h])])
        return model.embed(ids.unsqueeze(0))[0, -2:]
    def train_input(steps=3000, lr=3e-2):
        base = model.embed(context_ids(facts[:NF], 0, HOP1).unsqueeze(0))[0, :-2].detach()
        P = nn.Parameter(base.clone() + 0.0)
        opt = torch.optim.Adam([P], lr)
        Q = torch.stack([query_part(q, h) for q, h, _ in one_q]).detach()
        A = torch.tensor([a for *_, a in one_q])
        for s in range(steps):
            x = torch.cat([P.unsqueeze(0).expand(len(Q), -1, -1), Q], 1)
            loss = F.cross_entropy(model.run(x), A); opt.zero_grad(); loss.backward(); opt.step()
        return P.detach()
    P = train_input()
    def ask_input(qs):
        Q = torch.stack([query_part(q, h) for q, h, _ in qs])
        with torch.no_grad():
            return model.run(torch.cat([P.unsqueeze(0).expand(len(Q), -1, -1), Q], 1)).argmax(1)
    res["KB as input (frozen model)"] = ((ask_input(one_q) == torch.tensor([a for *_, a in one_q])).float().mean().item(),
                                         (ask_input(two_q) == torch.tensor([a for *_, a in two_q])).float().mean().item())
    unchanged = all(torch.equal(frozen[k], v) for k, v in model.state_dict().items())

    # fine-tune: change weights on the one-step questions, empty (padding) window
    import copy
    ft = copy.deepcopy(model); ft.train()
    for p in ft.parameters(): p.requires_grad_(True)
    opt = torch.optim.AdamW(ft.parameters(), 3e-4)
    pad = torch.full((NF, 2), 0)
    X1 = torch.stack([torch.cat([pad.flatten(), torch.tensor([q, h])]) for q, h, _ in one_q]); A1 = torch.tensor([a for *_, a in one_q])
    X2 = torch.stack([torch.cat([pad.flatten(), torch.tensor([q, h])]) for q, h, _ in two_q]); A2 = torch.tensor([a for *_, a in two_q])
    for s in range(1500):
        loss = F.cross_entropy(ft(X1), A1); opt.zero_grad(); loss.backward(); opt.step()
    ft.eval()
    with torch.no_grad():
        res["fine-tune weights"] = ((ft(X1).argmax(1) == A1).float().mean().item(), (ft(X2).argmax(1) == A2).float().mean().item())

    print(f"{'method':<28}{'taught 1-step':>14}{'never-asked 2-step':>20}")
    for k in ("oracle context", "RAG, one round", "RAG, two rounds", "fine-tune weights", "KB as input (frozen model)"):
        print(f"{k:<28}{res[k][0]:>14.3f}{res[k][1]:>20.3f}")
    print(f"\nchance {1/E:.3f}.  Frozen model unchanged after learning the input: {unchanged}")

if __name__ == "__main__":
    main()
