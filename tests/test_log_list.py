# tests/test_log_list.py
def test_log_list(client):
    response = client.get("/log-list")
    assert response.status_code == 200
    # Assuming an empty response for now, adjust as per your API logic
    assert response.json()