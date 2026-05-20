---
paths: "**/*.py"
---

# Python Guidelines

## Package Management
- **New projects**: Use `uv` with pyproject.toml and `uv sync` for dependencies
- **Existing projects**: May use setup.py - migration to uv is optional
- Every Python project has its own virtual environment (.venv)
- Run scripts with `uv run` or activate venv first

## Code Quality
- Type all Python code in 3.11+ style
- Lint: `uvx ruff check --fix .`
- Format: `uvx ruff format .`
- Type check: `uvx ty check .`
- **IMPORTANT**: Avoid local/lazy imports inside functions (except to prevent circular imports)
- Review and update docstrings in files you create or change

## Testing
- Keep tests in `/tests` folder
- Add tests for every new feature or bug fix
- Run with: `source .venv/bin/activate && pytest`
- Run tests before committing

## Pre-commit
- If configured: hooks run ruff and ty automatically
- If not configured: manually run `uvx ruff check --fix . && uvx ruff format . && uvx ty check .`
