FROM python:3.11.11-slim-bookworm

ARG VERSION=0.0.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=$VERSION

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project

COPY ./src /app/src
COPY ./testing /app/testing

COPY ./pyproject.toml ./uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

WORKDIR /app/testing

CMD ["glow", "--conf", "glow", "testcases/dev/test_load_dev.py"]