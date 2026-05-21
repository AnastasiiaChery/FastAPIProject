from fastapi.testclient import TestClient


def test_create_item_with_valid_body_returns_201(client: TestClient):
    response = client.post("/items", json={"name": "Widget"})
    assert response.status_code == 201


def test_create_item_with_valid_body_returns_item_with_id(client: TestClient):
    response = client.post("/items", json={"name": "Widget"})
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Widget"
    assert body["description"] is None


def test_create_item_with_description_returns_description(client: TestClient):
    response = client.post("/items", json={"name": "Widget", "description": "A thing"})
    assert response.json()["description"] == "A thing"


def test_create_item_ids_are_sequential(client: TestClient):
    r1 = client.post("/items", json={"name": "A"})
    r2 = client.post("/items", json={"name": "B"})
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


def test_create_item_with_missing_name_returns_422(client: TestClient):
    response = client.post("/items", json={"description": "no name"})
    assert response.status_code == 422


def test_create_item_with_empty_name_returns_422(client: TestClient):
    response = client.post("/items", json={"name": ""})
    assert response.status_code == 422


def test_create_item_with_name_too_long_returns_422(client: TestClient):
    response = client.post("/items", json={"name": "x" * 101})
    assert response.status_code == 422


def test_create_item_with_name_exactly_100_chars_returns_201(client: TestClient):
    response = client.post("/items", json={"name": "x" * 100})
    assert response.status_code == 201


def test_list_items_returns_empty_list_when_none(client: TestClient):
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_returns_all_created_items(client: TestClient):
    client.post("/items", json={"name": "A"})
    client.post("/items", json={"name": "B"})
    response = client.get("/items")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["A", "B"]


def test_get_item_returns_200_when_found(client: TestClient):
    client.post("/items", json={"name": "Widget"})
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_returns_404_when_not_found(client: TestClient):
    response = client.get("/items/999")
    assert response.status_code == 404


def test_delete_item_returns_204_when_found(client: TestClient):
    client.post("/items", json={"name": "Widget"})
    response = client.delete("/items/1")
    assert response.status_code == 204


def test_delete_item_removes_item_from_store(client: TestClient):
    client.post("/items", json={"name": "Widget"})
    client.delete("/items/1")
    response = client.get("/items/1")
    assert response.status_code == 404


def test_delete_item_returns_404_when_not_found(client: TestClient):
    response = client.delete("/items/999")
    assert response.status_code == 404
