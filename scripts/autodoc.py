import urllib.request
import json

"""
This file will create a readme file with all the endpoints and its usage with example cURL command.
Usage :
1. Run the project (This will create openapi.json serving in localhost:8000/openapi.json)
2. Run this script to create the documentation and validate is everything looks good

Sample .env file (To be saved in app root dir)

```
ad_server=
ad_username=
ad_password=
ad_domain=
ad_basecn=
```

"""

# URL of the OpenAPI spec
url = "http://127.0.0.1:8000/openapi.json"

# Fetch the OpenAPI spec
with urllib.request.urlopen(url) as response:
    data = response.read().decode("utf-8")

# Convert JSON string to Python dictionary
openapi_data = json.loads(data)

# Extract endpoints and parameters
endpoints = []
schemas = openapi_data['components'].get('schemas', {})

# Prepare constant content section
constant_content = """
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
"""

# Function to generate sample request body


def generate_sample_body(sample_schema) -> object:
    """

    @rtype: object
    """
    if 'properties' in sample_schema:
        body = {}
        for props, props_details in sample_schema['properties'].items():
            if 'type' in props_details:
                # Generate a sample value based on type
                if props_details['type'] == 'string':
                    body[props] = "sample_value"
                elif props_details['type'] == 'integer':
                    body[props] = 123
                elif props_details['type'] == 'boolean':
                    body[props] = True
                elif props_details['type'] == 'array':
                    body[props] = [1, 2, 3]
                else:
                    body[props] = None
        return json.dumps(body, indent=2)  # Return JSON formatted string
    return "{}"  # Empty body if no properties found


# Prepare content for the API Endpoints section
endpoint_content = "## API Endpoints\n\n"
for path, methods in openapi_data['paths'].items():
    for method, details in methods.items():
        endpoint_info = {
            "path": path,
            "method": method.upper(),
            "summary": details.get("summary", "No description provided"),
            "description": details.get("description", "No description provided"),
            "parameters": [],
            "responses": details.get("responses", {}),
            "requestBody": details.get("requestBody", {}),
            "curl_command": ""
        }

        # Process parameters only if present
        if 'parameters' in details and details['parameters']:
            for param in details['parameters']:
                param_info = {
                    "name": param["name"],
                    "in": param["in"],
                    "description": param.get("description", "No description"),
                    "required": param.get("required", False),
                    "schema_ref": None,
                }

                # If parameter schema is a reference, resolve it and create a link
                if "schema" in param and "$ref" in param["schema"]:
                    ref = param["schema"]["$ref"]
                    schema_name = ref.split("/")[-1]  # Get the schema name
                    param_info["schema_ref"] = f"[{
                        schema_name}](#{schema_name.lower()})"  # Create the link

                endpoint_info["parameters"].append(param_info)

        # Process request body only if present
        if 'requestBody' in details and 'content' in details['requestBody']:
            for content_type, content in details['requestBody']["content"].items():
                if "schema" in content and "$ref" in content["schema"]:
                    ref = content["schema"]["$ref"]
                    schema_name = ref.split("/")[-1]  # Get the schema name
                    # Generate a sample body for the request
                    if schema_name in schemas:
                        sample_body = generate_sample_body(
                            schemas[schema_name])
                        endpoint_info["requestBody"] = f"[{schema_name}](#{schema_name.lower()})\n\n```json\n{
                            sample_body}\n```"  # Embed the JSON body

        # Generate the cURL command for the endpoint
        curl_command = f"curl -X {endpoint_info['method']
                                  } 'http://127.0.0.1:8000{path}'"

        # Add parameters to the cURL command if there are query parameters
        if endpoint_info["parameters"]:
            for param in endpoint_info["parameters"]:
                if param["in"] == "query" and param["required"]:
                    # Add cURL command
                    endpoint_content += f"  - **cURL Command**:\n    ```bash\n    {
                        curl_command}\n    ```\n\n"

        # Add body to the cURL command if there's a request body
        if endpoint_info["requestBody"]:
            # Use the generated sample body
            # noinspection PyUnboundLocalVariable
            curl_command += f" -H 'Content-Type: application/json' -d '{
                json.dumps(sample_body).replace('\\n', '').replace('\\', '')}'"

        endpoint_info["curl_command"] = curl_command

        endpoints.append(endpoint_info)

        # Add endpoint content in markdown
        endpoint_content += f"### {endpoint_info['method']
                                   } {endpoint_info['path']}\n"
        endpoint_content += f"  - **Summary**: {endpoint_info['summary']}\n"
        endpoint_content += f"  - **Description**: {
            endpoint_info['description']}\n"

        # Process parameters section
        if endpoint_info['parameters']:
            endpoint_content += f"  - **Parameters**:\n"
            for param in endpoint_info["parameters"]:
                endpoint_content += f"    - **{param['name']
                                               }** (in {param['in']})\n"
                if param['schema_ref']:
                    endpoint_content += f"      - Schema Reference: {
                        param['schema_ref']}\n"
                if param['description']:
                    endpoint_content += f"      - Description: {
                        param['description']}\n"
                endpoint_content += f"      - Required: {param['required']}\n"

        # Process request body section
        if endpoint_info["requestBody"]:
            endpoint_content += f"  - **Request Body**: {
                endpoint_info['requestBody']}\n"

        # Process responses section
        if endpoint_info["responses"]:
            endpoint_content += f"  - **Responses**:\n"
            for status_code, response in endpoint_info["responses"].items():
                endpoint_content += f"    - **Status Code**: {status_code}\n"
                if "description" in response:
                    endpoint_content += f"      - **Description**: {
                        response['description']}\n"
                if "content" in response and "application/json" in response["content"]:
                    content = response["content"]["application/json"]
                    if "schema" in content and "$ref" in content["schema"]:
                        ref = content["schema"]["$ref"]
                        schema_name = ref.split("/")[-1]
                        endpoint_content += f"      - **Schema Reference**: [{
                            schema_name}](#{schema_name.lower()})\n"

        # Add cURL command
        endpoint_content += f"  - **cURL Command**:\n    ```bash\n    {
            curl_command}\n    ```\n\n"

# Prepare content for the schema section
schema_content = "## Schema Section\n\n"
if schemas:
    for schema_name, schema in schemas.items():
        schema_content += f"### {schema_name.lower()}\n"

        if 'type' in schema:
            schema_content += f"  - **Type**: {schema['type']}\n"
        if 'properties' in schema:
            schema_content += "  - **Properties**:\n"
            for prop, prop_details in schema['properties'].items():
                schema_content += f"    - **{
                    prop}** ({prop_details.get('type', 'unknown')})\n"
                schema_content += f"      - Description: {
                    prop_details.get('title', 'No description')}\n"
                if 'enum' in prop_details:
                    schema_content += f"      - Enum: {
                        ', '.join(prop_details['enum'])}\n"
                if 'default' in prop_details:
                    schema_content += f"      - Default: {
                        prop_details['default']}\n"
        schema_content += "\n"
else:
    schema_content += "No schemas found in the OpenAPI spec.\n"

# Write everything to the README file
readme_content = constant_content + endpoint_content + schema_content

# Path to your README file
readme_file_path = "../README.md"

# Clear the README file content before writing fresh content
with open(readme_file_path, "w") as file:
    file.write(readme_content)

print("README updated with the latest API endpoints, schema information, responses, and cURL examples.")
