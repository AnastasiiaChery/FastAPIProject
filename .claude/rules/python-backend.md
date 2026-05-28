---
paths: "**/*.py"
applies_to: ["implementer", "code-reviewer", "test-writer", "planner"]
language: python
version: "3.11+"
---

# Python Backend Best Practices

This document is the **single source of truth** for Python backend development standards. All agents (implementer, code-reviewer, test-writer, planner) must follow these rules.

## Security Rules (CRITICAL)

These are non-negotiable. Violations are BLOCKER-level issues.

- ❌ **NEVER** use `eval()` or `exec()` on user input
- ❌ **NEVER** use string concatenation for SQL queries
- ✅ **ALWAYS** use parameterized queries for database operations
- ✅ **ALWAYS** validate and sanitize user inputs at entry points (API boundaries, CLI args, file uploads)
- ✅ **ALWAYS** clean up resources with context managers (`with` statements)
- ❌ **NEVER** include secrets, API keys, or credentials in code
- ✅ **ALWAYS** ensure `.gitignore` includes: `.env`, `*.pem`, `*credentials*`, `*secret*`
- ✅ **ALWAYS** review code for OWASP Top 10 vulnerabilities before committing

### Security Examples

**❌ Bad:**
```python
# SQL injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# Code injection vulnerability
eval(user_input)

# Unvalidated shell command
os.system(f"rm {filename}")
```

**✅ Good:**
```python
# Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# Input validation before shell command
if not re.match(r'^[a-zA-Z0-9_-]+$', filename):
    raise ValueError("Invalid filename")
subprocess.run(["rm", filename], check=True)
```

## Code Quality Standards

### Style and Type Hints
- Follow **PEP 8** style guide strictly
- Use **type hints** for all function signatures (PEP 484)
- Modern syntax: `list[str]`, `dict[str, int]` (Python 3.9+ style)
- Import `Any`, `Optional`, etc. from `typing` when needed

```python
from typing import Any, Optional

def process_data(
    input_data: list[dict[str, Any]],
    threshold: float = 0.5
) -> dict[str, Any]:
    """Process input data and return aggregated results."""
    ...
```

### Documentation
- Write **docstrings** for all public modules, classes, and functions
- Use **Google style** docstrings consistently:

```python
def calculate_discount(price: float, percentage: float) -> float:
    """Calculate discounted price.

    Args:
        price: Original price in dollars
        percentage: Discount percentage (0-100)

    Returns:
        Final price after discount

    Raises:
        ValueError: If percentage is not between 0 and 100
    """
    if not 0 <= percentage <= 100:
        raise ValueError(f"Invalid percentage: {percentage}")
    return price * (1 - percentage / 100)
```

### Code Structure
- Keep functions **focused and single-purpose** (max 50 lines when possible)
- Use **descriptive variable names** that reveal intent
- Avoid **magic numbers** — use named constants
- Prefer **composition over inheritance**
- Use **dataclasses** or **Pydantic models** for structured data

```python
from dataclasses import dataclass
from typing import Protocol

# Use Protocol for interfaces
class DataProcessor(Protocol):
    """Interface for data processing implementations."""
    def process(self, data: bytes) -> dict[str, Any]: ...

# Use dataclass for data structures
@dataclass
class Configuration:
    """Application configuration."""
    api_key: str
    timeout: int = 30
    retry_count: int = 3
```

### Import Rules
- ❌ **AVOID** local/lazy imports inside functions (except to prevent circular imports)
- ✅ **ALWAYS** place imports at module level
- Group imports: stdlib → third-party → local
- Use absolute imports over relative imports

```python
# ✅ Good: imports at module level
from typing import Any
import json
from myapp.models import User

def process_user(data: dict[str, Any]) -> User:
    return User(**data)
```

```python
# ❌ Bad: lazy import (avoid unless circular import)
def process_user(data: dict[str, Any]):
    from myapp.models import User  # Don't do this
    return User(**data)
```

## Package Management

### Modern Python Projects (Use `uv`)
- Use **`uv`** with `pyproject.toml` for new projects
- Every project has its own **virtual environment** (`.venv`)
- Install dependencies: `uv add <package>`
- Run scripts: `uv run <script>` or activate venv first
- Sync dependencies: `uv sync`

### Legacy Projects
- May use `setup.py` — migration to `uv` is optional
- Still require virtual environment per project
- Document package manager in README

## Linting & Formatting

Run these before every commit:

```bash
# Lint and auto-fix issues
uvx ruff check --fix .

# Format code
uvx ruff format .

# Type check
uvx ty check .
```

### Pre-commit Hooks
- If `.pre-commit-config.yaml` exists: hooks run automatically
- If not configured: manually run the commands above
- **ALWAYS** run linting/formatting before committing

## Testing Standards

### Test Organization
- Keep tests in **`/tests`** folder
- **Mirror source structure**: `app/users.py` → `tests/test_users.py`
- Use **pytest** as the test framework
- Run tests: `source .venv/bin/activate && pytest`

### Test Design Principles
- **One test per behavior** — not one test per function
- **Test the contract** (inputs → outputs, side effects), not implementation details
- **AAA structure** — every test follows Arrange / Act / Assert (with blank lines between)
- **Name tests clearly**: `test_<what>_<when>_<expected>`

```python
def test_create_user_with_duplicate_email_returns_409():
    # Arrange
    existing_user = User(email="test@example.com", name="Existing")
    db.save(existing_user)

    # Act
    response = create_user(email="test@example.com", name="Duplicate")

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.error_message
```

### Test Coverage
- **Minimum: 80% line coverage** on all new or changed files
- Verify with: `pytest --cov=<module> --cov-report=term-missing`
- Cover these cases for every function:
  - ✅ Happy path — expected inputs produce expected output
  - ✅ Boundary values — min/max inputs, empty collections, zero
  - ✅ Invalid input — wrong type, missing field, out-of-range value
  - ✅ Error cases — external dependency fails, resource not found
  - ✅ Side effects — database state, cache invalidation, events

### Parameterization
- Use `@pytest.mark.parametrize` when **3+ test cases** differ only in values:

```python
import pytest

@pytest.mark.parametrize("price,percentage,expected", [
    (100.0, 10.0, 90.0),
    (50.0, 20.0, 40.0),
    (200.0, 0.0, 200.0),
])
def test_calculate_discount_returns_correct_value(price, percentage, expected):
    result = calculate_discount(price, percentage)
    assert result == expected
```

### Fixtures
- Extract setup into **`@pytest.fixture`** only if reused in **2+ tests**
- Prefer **inline setup** over DRY at the test level (readability > reusability)
- **Never mock** the unit under test itself
- **Only mock** external dependencies (HTTP calls, databases, queues, clocks)

### Test Isolation
- Every test **must be independent**
- No shared mutable state between tests
- Use fixtures for test-specific setup/teardown

## Error Handling

### Exception Best Practices
- Use **specific exception types**, never bare `except:`
- **Raise exceptions** for exceptional cases
- **Return error values** for expected failures
- Include **context** in exception messages
- Use **custom exception classes** for domain-specific errors

```python
# ✅ Good: specific exceptions with context
class InsufficientFundsError(Exception):
    """Raised when account has insufficient funds."""
    pass

def withdraw(account: Account, amount: float) -> None:
    if amount > account.balance:
        raise InsufficientFundsError(
            f"Cannot withdraw ${amount}, balance is ${account.balance}"
        )
    account.balance -= amount
```

```python
# ❌ Bad: bare except, no context
try:
    withdraw(account, amount)
except:  # Don't do this
    pass  # Silent failure
```

### Resource Management
- **ALWAYS** use context managers for resource cleanup:

```python
# ✅ Good: context manager ensures cleanup
with open(filename, 'r') as f:
    data = f.read()

# ✅ Good: custom context manager
from contextlib import contextmanager

@contextmanager
def database_connection(url: str):
    conn = connect(url)
    try:
        yield conn
    finally:
        conn.close()
```

## Architecture Patterns

### Separation of Concerns
- **Separate business logic from I/O operations**
- Pure functions when possible (easier to test)
- Make side effects explicit and mockable

```python
# ✅ Good: testable business logic
def calculate_order_total(items: list[Item], tax_rate: float) -> float:
    """Pure function - easy to test."""
    subtotal = sum(item.price * item.quantity for item in items)
    return subtotal * (1 + tax_rate)

def process_order(order_id: str, db: Database) -> None:
    """I/O operation - depends on external database."""
    order = db.get_order(order_id)
    total = calculate_order_total(order.items, order.tax_rate)
    db.update_order(order_id, total=total)
```

### Dependency Injection
- Write testable code using dependency injection
- Pass dependencies as parameters, don't hardcode them

```python
# ✅ Good: injectable dependency
def send_notification(user: User, mailer: EmailService) -> None:
    mailer.send(user.email, "Welcome!")

# ❌ Bad: hardcoded dependency
def send_notification(user: User) -> None:
    from myapp.email import default_mailer  # Hard to test
    default_mailer.send(user.email, "Welcome!")
```

### Data Structures
- Use **dataclasses** for simple data structures
- Use **Pydantic** for data validation and API models
- Prefer **immutable data** when possible (frozen dataclasses)

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field

# Simple data structure
@dataclass(frozen=True)
class Point:
    x: float
    y: float

# API model with validation
class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)
```

## Quality Checklist

Before delivering code, verify:

- [ ] All security rules followed (no eval/exec, parameterized SQL, validated inputs)
- [ ] All functions have type hints
- [ ] All public APIs have docstrings (Google style)
- [ ] Error handling uses specific exceptions with context
- [ ] No hardcoded secrets or credentials
- [ ] Resources managed with context managers
- [ ] Code follows PEP 8 (run `uvx ruff check`)
- [ ] Types validated (run `uvx ty check`)
- [ ] Code is testable (dependencies injectable, logic separated from I/O)
- [ ] Tests written for all new logic (80%+ coverage)
- [ ] All tests pass (`pytest`)
- [ ] No local/lazy imports (except circular import fixes)
- [ ] Related documentation updated

## Anti-Patterns to Avoid

| ❌ Don't | ✅ Do |
|---------|-------|
| Bare `except:` clauses | Specific exception types |
| String concatenation for SQL | Parameterized queries |
| Magic numbers in code | Named constants |
| God classes (1000+ lines) | Small, focused classes |
| Mocking the unit under test | Mock only external dependencies |
| Local imports in functions | Module-level imports |
| `eval()` on user input | Proper parsing/validation |
| Silent failures (empty except) | Explicit error handling |
| Inheritance for code reuse | Composition |
| Global mutable state | Dependency injection |

---

**Last updated:** 20260522
**Python version:** 3.11+
**Test framework:** pytest
**Linter/Formatter:** ruff
**Type checker:** ty