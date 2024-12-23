import os
import re
from collections import defaultdict

# Define the error code pattern (uppercase letters, underscores, followed by 3 digits)
ERROR_CODE_PATTERN = r'[A-Z_]+_\d{3}'

# Regex patterns for matching comments
SINGLE_LINE_COMMENT_PATTERN = r'#.*'
MULTI_LINE_COMMENT_PATTERN = r"'''(.*?)'''|\"\"\"(.*?)\"\"\""

# Flag to control whether HTTP error codes should be included
include_http_error_codes = False  # Change this to True to include HTTP error codes

def remove_comments(content: str):
    """
    Removes single-line and multi-line comments from the content.
    """
    # Remove single-line comments
    content = re.sub(SINGLE_LINE_COMMENT_PATTERN, '', content)
    # Remove multi-line comments
    content = re.sub(MULTI_LINE_COMMENT_PATTERN, '', content, flags=re.DOTALL)
    return content


def find_error_codes_in_file(file_path: str):
    """
    Extracts all error codes from a file using regex and returns a list of tuples (error_code, file_path).
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove comments from the content
    content = remove_comments(content)

    # Find all matching error codes
    error_codes = re.findall(ERROR_CODE_PATTERN, content)

    # If HTTP error codes should not be included, filter them out
    if not include_http_error_codes:
        error_codes = [code for code in error_codes if not code.startswith('HTTP_')]

    return error_codes


def scan_project_for_error_codes(project_directory: str):
    """
    Scans all Python files in a project directory for custom error codes, ignoring specified directories.
    """
    error_codes = defaultdict(list)

    # Traverse all files in the directory and subdirectories
    for root, dirs, files in os.walk(project_directory):
        # Exclude the 'venv' directory (or any other directories you want to ignore)
        if '.venv' in dirs:
            dirs.remove('.venv')

        for file in files:
            if file.endswith(".py"):  # Only scan Python files
                file_path = os.path.join(root, file)
                file_error_codes = find_error_codes_in_file(file_path)
                for error_code in file_error_codes:
                    error_codes[error_code].append(file_path)

    return error_codes


def check_for_duplicate_error_codes(error_codes):
    """
    Check for duplicate error codes and return a list of duplicates with file locations.
    """
    duplicates = {code: files for code, files in error_codes.items() if len(files) > 1}
    return duplicates


def main():
    """
    Main function to scan the current directory and check for duplicate error codes.
    """
    current_directory = os.getcwd()  # Get the current working directory
    print(f"Scanning current directory: {current_directory}")

    # Step 1: Scan the current directory for error codes
    error_codes = scan_project_for_error_codes(current_directory)

    # Step 2: Check for duplicates
    duplicates = check_for_duplicate_error_codes(error_codes)

    if duplicates:
        print(f"Duplicate error codes found:\n")
        for code, files in duplicates.items():
            print(f"{code}: {len(files)} occurrences found in files:")
            for file in files:
                print(f"  - {file}")
    else:
        print("No duplicate error codes found.")


# Run the script
if __name__ == "__main__":
    main()
