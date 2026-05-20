---
paths: "**/Dockerfile*"
---

# Dockerfile Guidelines

## Base Images
- Use specific version tags, never `latest` — e.g. `python:3.11-slim`
- Prefer `slim` or `alpine` variants to reduce image size
- Use official images from Docker Hub

## Layer Caching
- Order instructions from least to most frequently changed
- Copy dependency files (`pyproject.toml`, `uv.lock`) before source code
- Run `uv sync` before `COPY . .` so deps are cached independently of code changes

## Security
- Run as non-root: add `RUN useradd -m app && USER app`
- Never store secrets in the image — use env vars or secrets at runtime
- Use `.dockerignore` to exclude `.venv`, `.git`, `__pycache__`, `.env`

## Best Practices
- One process per container
- Use `ENTRYPOINT` for the command, `CMD` for default arguments
- Set `WORKDIR` explicitly, don't rely on default `/`
- Use multi-stage builds to keep final image free of build tools
