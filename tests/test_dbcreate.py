# tests/test_dbcreate.py
def test_dbcreate(client):
    response = client.post("/dbcreate")
    assert response.status_code == 201
    assert response.json() == {"message": "Database created"}  # Modify based on your actual response
