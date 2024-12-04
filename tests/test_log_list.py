# tests/test_log_list.py
def test_log_list(client):
    response = client.get("/log-list")
    assert response.status_code == 200
    # Assuming an empty response for now, adjust as per your API logic
    assert response.json() == {'loggers': [{'level': 'NOTSET', 'logger_name': 'concurrent.futures'},
             {'level': 'NOTSET', 'logger_name': 'concurrent'},
             {'level': 'NOTSET', 'logger_name': 'asyncio'},
             {'level': 'NOTSET', 'logger_name': 'fastapi'},
             {'level': 'NOTSET', 'logger_name': 'httpx'},
             {'level': 'NOTSET', 'logger_name': 'rich'},
             {'level': 'NOTSET', 'logger_name': 'uvicorn.error'},
             {'level': 'NOTSET', 'logger_name': 'uvicorn'},
             {'level': 'NOTSET', 'logger_name': 'watchfiles.watcher'},
             {'level': 'NOTSET', 'logger_name': 'watchfiles'},
             {'level': 'ERROR', 'logger_name': 'watchfiles.main'},
             {'level': 'DEBUG', 'logger_name': 'homeops'},
             {'level': 'DEBUG', 'logger_name': 'homeops.db'},
             {'level': 'DEBUG', 'logger_name': 'homeops.app'},
             {'level': 'NOTSET', 'logger_name': 'ldap3'},
             {'level': 'DEBUG', 'logger_name': 'pyasn1'},
             {'level': 'NOTSET', 'logger_name': 'homeops.ad'}]}
