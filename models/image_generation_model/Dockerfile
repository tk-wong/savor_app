FROM nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=auto \          
    WORKDIR=/app\
    UV_NO_DEV=1\
    VIRTUAL_ENV="/app/.venv"

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /app/.venv && uv sync --locked --no-dev --no-install-project 

COPY main.py image_generation_model.py /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM nvidia/cuda:13.0.2-cudnn-runtime-ubuntu24.04

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py /app/image_generation_model.py /app/
COPY --from=builder /root/.local/share/uv/python /root/.local/share/uv/python
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1\
    PATH="/app/.venv/bin:$PATH"\
    VIRTUAL_ENV="/app/.venv"

EXPOSE 5020
RUN ls -la /app/.venv/bin
CMD ["python", "main.py"]

