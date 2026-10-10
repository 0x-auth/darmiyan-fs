# darmiyan -- a two-chart emulator for self-referential relations.
#
# The image is deliberately plain. Nothing here accelerates anything, bends
# any clock, or contains any moment. It is Debian, Python, and one package.
# The only unusual thing is that /var/darmiyan is where relations get
# written as directories and symlinks, and that needs a real filesystem --
# which is the entire reason this is a container rather than a library.

FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="darmiyan"
LABEL org.opencontainers.image.description="Two-chart emulator for self-referential relations"
LABEL org.opencontainers.image.version="1.1.0"

# A real filesystem for the artifacts. tmpfs would work too; what must NOT
# be used is anything that resolves symlinks differently from the host
# kernel, because the inside resolver's failures are the output.
RUN mkdir -p /var/darmiyan
VOLUME /var/darmiyan

WORKDIR /opt/darmiyan
COPY pyproject.toml README.md ./
COPY darmiyan ./darmiyan
RUN pip install --no-cache-dir -e .

# Prove the contract at build time. If the bridge cannot refuse, the image
# does not get built.
RUN darmiyan verify

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["darmiyan"]
CMD ["suite"]
