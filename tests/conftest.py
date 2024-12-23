import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    # Use application/x-www-form-urlencoded format for the request
    data = {
        "username": "homeops",  # Adjust username if necessary
        "password": "Passw0rd"  # Adjust password if necessary
    }
    response = client.post(
        "/token",
        data=data,
        headers={"accept": "application/json"}
    )

    assert response.status_code == 200
    return response.json()["access_token"]