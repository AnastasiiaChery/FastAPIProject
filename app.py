from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class HealthResponse(BaseModel):
    status: str


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


_items: dict[int, Item] = {}
_next_id: int = 1


def reset_items() -> None:
    global _next_id
    _items.clear()
    _next_id = 1


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/items", response_model=Item, status_code=201)
def create_item(body: ItemCreate) -> Item:
    global _next_id
    item = Item(id=_next_id, name=body.name, description=body.description)
    _items[_next_id] = item
    _next_id += 1
    return item


@app.get("/items", response_model=list[Item])
def list_items() -> list[Item]:
    return list(_items.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
