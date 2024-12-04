# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.app import app  # Assuming your FastAPI app is in app/app.py

@pytest.fixture
def client():
    return TestClient(app)