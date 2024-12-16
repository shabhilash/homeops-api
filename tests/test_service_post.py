# tests/test_service_post.py
def test_service_post(client):
    response = client.post("/service")
    assert response.status_code == 200
    assert response.json()