import pathlib


def test_main_py_removed():
    assert not pathlib.Path("main.py").exists()


def test_setup_py_removed():
    assert not pathlib.Path("setup.py").exists()


def test_pyproject_has_no_anthropic():
    content = pathlib.Path("pyproject.toml").read_text()
    assert "anthropic" not in content
