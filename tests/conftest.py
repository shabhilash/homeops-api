# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is in app/main.py

@pytest.fixture
def client():
    return TestClient(app)