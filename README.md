
# homeops-api

## Project Overview

A tool for automating and managing homelab operations.

## API Endpoints

### GET /
  - **Summary**: Root endpoint to check if the service is running
  - **Description**: To test if the API is working 

Success Response
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/'
    ```

### PUT /reload/ad-users
  - **Summary**: Refresh Users
  - **Description**: This endpoint will sync all the AD users to the local database
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X PUT 'http://127.0.0.1:8000/reload/ad-users'
    ```

### POST /token
  - **Summary**: Login For Access Token
  - **Description**: No description provided
  - **Request Body**: [Body_login_for_access_token_token_post](#body_login_for_access_token_token_post)

```json
{
  "username": "sample_value",
  "password": "sample_value"
}
```
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
      - **Schema Reference**: [TokenResponse](#tokenresponse)
    - **Status Code**: 422
      - **Description**: Validation Error
      - **Schema Reference**: [HTTPValidationError](#httpvalidationerror)
  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/token' -H 'Content-Type: application/json' -d '"{  "username": "sample_value",  "password": "sample_value"}"'
    ```

  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/service'
    ```

  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/service'
    ```

### POST /service
  - **Summary**: Service Actions
  - **Description**: Systemctl actions for linux server 

**Supports** : *[start, stop, restart, reload, enable, disable]*
  - **Parameters**:
    - **svc** (in query)
      - Description: No description
      - Required: True
    - **action** (in query)
      - Schema Reference: [ServiceActions](#serviceactions)
      - Description: No description
      - Required: True
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
    - **Status Code**: 422
      - **Description**: Validation Error
      - **Schema Reference**: [HTTPValidationError](#httpvalidationerror)
  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/service'
    ```

  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/service'
    ```

### GET /service
  - **Summary**: Service Status
  - **Description**: Systemctl status for linux server 

**Supports** : *[status]*
  - **Parameters**:
    - **svc** (in query)
      - Description: No description
      - Required: True
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
    - **Status Code**: 422
      - **Description**: Validation Error
      - **Schema Reference**: [HTTPValidationError](#httpvalidationerror)
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/service'
    ```

### PUT /log-level
  - **Summary**: Modify Loggers on the go
  - **Description**: Endpoint to change the log level of a logger dynamically and update the config file. 

@type logger_level: object
  - **Request Body**: [LogLevel](#loglevel)

```json
{
  "logger_name": "sample_value",
  "level": "sample_value"
}
```
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
    - **Status Code**: 422
      - **Description**: Validation Error
      - **Schema Reference**: [HTTPValidationError](#httpvalidationerror)
  - **cURL Command**:
    ```bash
    curl -X PUT 'http://127.0.0.1:8000/log-level' -H 'Content-Type: application/json' -d '"{  "logger_name": "sample_value",  "level": "sample_value"}"'
    ```

### GET /log-list
  - **Summary**: Log List
  - **Description**: Endpoint to list all loggers and their current levels.
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/log-list'
    ```

## Schema Section

### body_login_for_access_token_token_post
  - **Type**: object
  - **Properties**:
    - **username** (string)
      - Description: Username
    - **password** (string)
      - Description: Password

### httpvalidationerror
  - **Type**: object
  - **Properties**:
    - **detail** (array)
      - Description: Detail

### loglevel
  - **Type**: object
  - **Properties**:
    - **logger_name** (string)
      - Description: Logger Name
    - **level** (string)
      - Description: Level

### serviceactions
  - **Type**: string

### tokenresponse
  - **Type**: object
  - **Properties**:
    - **access_token** (string)
      - Description: Access Token
    - **token_type** (string)
      - Description: Token Type
    - **expires_in** (integer)
      - Description: Expires In

### validationerror
  - **Type**: object
  - **Properties**:
    - **loc** (array)
      - Description: Location
    - **msg** (string)
      - Description: Message
    - **type** (string)
      - Description: Error Type

