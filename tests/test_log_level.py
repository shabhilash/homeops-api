# tests/test_log_level.py
def test_log_level(client):
    data = {
        "logger_name": "homeops.db",
        "level": "DEBUG"
    }
    response = client.post("/log-level", json=data)
    assert response.status_code == 200
    # You can add assertions based on how your endpoint responds
    assert response.json() == {'message': "Log level of logger 'homeops.db' set to DEBUG"}
