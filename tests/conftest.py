import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        "name": "Test Item",
        "description": "A test item",
        "price": 99.99,
        "tax_rate": 0.1
    }
