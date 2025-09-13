import pytest
from decimal import Decimal

def test_create_item(client, sample_item_data):
    """Test creating an item"""
    response = client.post("/api/v1/items/", json=sample_item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_item_data["name"]
    assert data["price"] == sample_item_data["price"]
    assert "id" in data

def test_get_items(client, sample_item_data):
    """Test getting all items"""
    # Create an item first
    client.post("/api/v1/items/", json=sample_item_data)
    
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert "average_price" in data
    assert "inventory_value" in data

def test_get_item_by_id(client, sample_item_data):
    """Test getting item by ID"""
    # Create an item first
    create_response = client.post("/api/v1/items/", json=sample_item_data)
    item_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == sample_item_data["name"]

def test_get_nonexistent_item(client):
    """Test getting non-existent item"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
