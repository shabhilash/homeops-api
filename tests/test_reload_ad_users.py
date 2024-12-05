# tests/test_reload_ad_users.py
def test_reload_ad_users(client):
    response = client.put("/reload/ad-users")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "Success"
    assert "details" in data
    assert "message" in data["details"]
    assert data["details"]["message"] == "Users Refreshed"
    assert "total_users" in data["details"]
    assert "new_users" in data["details"]
    assert "modified_users" in data["details"]

    # Ensure the values are integers
    assert isinstance(data["details"]["total_users"], int)
    assert isinstance(data["details"]["new_users"], int)
    assert isinstance(data["details"]["modified_users"], int)
