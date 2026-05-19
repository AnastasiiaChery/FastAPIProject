from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_main_py_removed():
    assert not (PROJECT_ROOT / "main.py").exists()


def test_setup_py_removed():
    assert not (PROJECT_ROOT / "setup.py").exists()


def test_pyproject_has_no_anthropic():
    pyproject = PROJECT_ROOT / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml not found"
    assert "anthropic" not in pyproject.read_text()
