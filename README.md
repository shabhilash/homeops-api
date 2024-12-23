
# homeops-api

## Project Overview

A tool for automating and managing homelab operations.

### Install
```shell
sudo HOMEOPS_DIR='/opt/homeops-api' bash -c "$(curl -sSL https://github.com/shabhilash/homeops-api/raw/main/helper_scripts/setup.sh)" -v -b 'main'
```
### Update
```shell
sudo HOMEOPS_DIR='/opt/homeops-api' bash -c "$(curl -sSL https://github.com/shabhilash/homeops-api/raw/main/helper_scripts/update.sh)" -v
```
### Uninstall
```shell
sudo HOMEOPS_DIR='/opt/homeops-api' bash -c "$(curl -sSL https://github.com/shabhilash/homeops-api/raw/main/helper_scripts/uninstall.sh)" -v 
```
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
      - **Description**: Invalid Password
      - **Schema Reference**: [ProblemDetails](#problemdetails)
    - **Status Code**: 404
      - **Description**: User Not Found
      - **Schema Reference**: [ProblemDetails](#problemdetails)
  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/token' -H 'Content-Type: application/json' -d '"{  "username": "sample_value",  "password": "sample_value"}"'
    ```

  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/server/service'
    ```

  - **cURL Command**:
    ```bash
    curl -X POST 'http://127.0.0.1:8000/server/service'
    ```

### POST /server/service
  - **Summary**: Service Actions
  - **Description**: Perform a systemctl action on a Linux server service.

Args:
    svc (str): The name of the service to perform the action on.
    action (str): The action to perform. Supported actions are: start, stop, restart, reload, enable, disable.
    current_user (User): The current authenticated user (injected by Depends).

Returns:
    dict: A dictionary with the status of the action, the action performed, and the service name.

Raises:
    CustomHTTPException: If the service action fails.
  - **Parameters**:
    - **svc** (in query)
      - Description: No description
      - Required: True
    - **action** (in query)
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
    curl -X POST 'http://127.0.0.1:8000/server/service'
    ```

  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/server/service'
    ```

### GET /server/service
  - **Summary**: Service Status
  - **Description**: Get the status of a Linux server service.

Args:
    svc (str): The name of the service to get the status for.

Returns:
    dict: A dictionary with the status of the service and the service name.

Raises:
    CustomHTTPException: If fetching the service status fails.
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
    curl -X GET 'http://127.0.0.1:8000/server/service'
    ```

### GET /server/disk-usage
  - **Summary**: Get All Disk Usage
  - **Description**: Endpoint to retrieve disk usage statistics using the 'df' command.

**Returns:**
- `disk_usage_list` (list): A list of dictionaries containing disk usage data.

**Raises:**
- `DiskCommandNotFoundError`: Raised when the 'df' command is not found.
- `DiskUsageFetchError`: Raised when there is a failure to fetch disk usage.
- `DiskUsageSubprocessError`: Raised if a subprocess error occurs.
- `DiskUsageFileNotFoundError`: Raised when a required file is not found.

**Error Codes:**
- `DISK_COMMAND_NOT_FOUND_001`: Raised when the 'df' command is not available on the system.
- `DISK_USAGE_FETCH_ERROR_001`: Raised when an error occurs while fetching disk usage.
- `DISK_USAGE_SUBPROCESS_ERROR_001`: Raised when a subprocess error occurs while running the 'df' command.
- `DISK_USAGE_FILE_NOT_FOUND_001`: Raised when the 'df' command or a required file is missing.
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/server/disk-usage'
    ```

### GET /server/cpu-usage
  - **Summary**: Get Cpu Usage
  - **Description**: Fetch and return detailed CPU usage statistics.

Returns:
    dict: A dictionary containing various CPU usage statistics.

Raises:
    HTTPException: If there is an error fetching or parsing CPU usage data.
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/server/cpu-usage'
    ```

### GET /server/memory-usage
  - **Summary**: Get Memory Usage
  - **Description**: Fetches and returns detailed memory usage statistics of the system. 


This function runs the 'free' command to gather memory and swap usage information
and parses the output. It calculates memory usage percentages, handles errors,
and returns the data in a structured format. 


Returns: 

    dict: A dictionary containing memory usage details including total, used,
          free, buffers, cached memory, and memory usage percentages. 

    - total_memory: Total physical memory 

    - used_memory: Memory currently used by processes 

    - free_memory: Unused memory 

    - buffers_memory: Memory used for file system buffers 

    - cached_memory: Memory used for caching data 

    - memory_usage_percent: Percentage of memory used 

    - total_swap: Total swap space 

    - used_swap: Swap space used 

    - free_swap: Unused swap space 


Raises: 

    HTTPException: If there's an error executing the 'free' command or parsing
                   the memory data. The exception will contain an appropriate status code.
  - **Responses**:
    - **Status Code**: 200
      - **Description**: Successful Response
  - **cURL Command**:
    ```bash
    curl -X GET 'http://127.0.0.1:8000/server/memory-usage'
    ```

### PUT /log-level
  - **Summary**: Modify Loggers on the go
  - **Description**: Endpoint to change the log level of a logger dynamically and update the config file.

**Parameters:**
- `logger_level` (LogLevel): The logger name and level to be changed.

**Returns:**
- `message` (str): A message indicating the result of the operation.

**Raises:**
- `InvalidLogLevel`: Raised when the log level provided is invalid.
- `LoggerNotFound`: Raised when the specified logger is not found in the logging manager.
- `LoggerUpdateError`: Raised when the logger update fails.

**Error Codes:**
- `INVALID_LOG_LEVEL_001`: Raised when an invalid log level is provided.
- `LOGGER_NOT_FOUND_002`: Raised when the logger is not found in the logging manager.
- `LOGGER_UPDATE_ERROR_002`: Raised when an error occurs during the update of the logger configuration.
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

**Returns:**
- `loggers` (list): A list of dictionaries containing logger names and their respective levels.

**Error Codes:**
- `LOGGER_NOT_FOUND_001`: Raised if a logger is not found in the logging manager.
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

### problemdetails
  - **Type**: object
  - **Properties**:
    - **type** (string)
      - Description: Type
    - **title** (string)
      - Description: Title
    - **status** (integer)
      - Description: Status
    - **detail** (string)
      - Description: Detail
    - **instance** (unknown)
      - Description: Instance
    - **code** (string)
      - Description: Code

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

