# tests/test_root.py
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'status': True}  # Assuming empty response as per your openapi
