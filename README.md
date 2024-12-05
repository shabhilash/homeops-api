
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

### POST /dbcreate
  - **Summary**: Create a new Database
  - **Description**: This endpoint will create a database if not present and creates tables [users]
  - **Responses**:
    - **Status Code**: 201
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/dbcreate'
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

### validationerror
  - **Type**: object
  - **Properties**:
    - **loc** (array)
      - Description: Location
    - **msg** (string)
      - Description: Message
    - **type** (string)
      - Description: Error Type

