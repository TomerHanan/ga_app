from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_read_item():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}


def test_read_item_with_query():
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}


def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Laptop", "description": "A powerful laptop", "price": 999.99, "tax": 50.0}
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Laptop",
        "description": "A powerful laptop",
        "price": 999.99,
        "tax": 50.0,
        "price_with_tax": 1049.99
    }


def test_create_item_without_tax():
    response = client.post(
        "/items/",
        json={"name": "Mouse", "price": 25.99}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mouse"
    assert data["price"] == 25.99
    assert "price_with_tax" not in data


def test_create_item_invalid_data():
    response = client.post(
        "/items/",
        json={"name": "Invalid Item"}  # Missing required 'price' field
    )
    assert response.status_code == 422  # Unprocessable Entity