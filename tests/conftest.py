import pytest
from fastapi.testclient import TestClient
from app import app, reset_items


@pytest.fixture(autouse=True)
def _reset_items():
    reset_items()
    yield
    reset_items()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
