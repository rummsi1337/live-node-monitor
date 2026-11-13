FROM python:3.15-slim as builder

COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv
RUN mkdir -p /app
COPY . /app

WORKDIR /app
RUN uv sync --locked --no-dev

FROM python:3.15-slim as base

COPY --from=builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "/app/src/main.py", "--config", "/app/config.yaml"]
