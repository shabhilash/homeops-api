def test_log_level(client, auth_token):
    data = {
        "logger_name": "homeops.db",
        "level": "info"
    }
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = client.put("/log-level", json=data, headers=headers)

    # Print the entire response object (less readable)
    print("Response object:", response)

    # Print the response status code and body
    print("Response status code:", response.status_code)
    print("Response body:", response.json())

    assert response.status_code == 200
    assert response.json() == {'message': "Log level of logger 'homeops.db' set to INFO"}
