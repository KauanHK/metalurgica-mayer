# Build em dois estágios: as dependências são instaladas num estágio com
# compilador e só o venv pronto atravessa para a imagem final — que fica sem
# build-essential, sem cache do uv e sem o material de compilação.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# O lock entra junto e manda no build: `--locked` falha se ele estiver
# dessincronizado do pyproject, em vez de resolver versões novas na hora e gerar
# uma imagem diferente da que foi testada.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

FROM python:3.14-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

# Usuário sem privilégios: um processo comprometido não deve poder escrever na
# própria imagem.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
