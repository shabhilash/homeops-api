# tests/test_reload.py
def test_reload_ad_users(client):
    response = client.put("/reload/ad-users")
    assert response.status_code == 204  # No content expected on success
