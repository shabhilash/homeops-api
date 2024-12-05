# tests/test_log_level_error.py
def test_log_level_validation_error(client):
    data = {"logger_name": "test_logger"}  # Missing "level"
    response = client.put("/log-level", json=data)
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()  # Ensure that the validation error is returned
