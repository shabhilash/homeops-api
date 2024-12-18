#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_DIR="/path/to/your/project"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/homeops-api.service"
USER=$(whoami)
REQUIRED_PYTHON_VERSION="3.8"
LOG_FILE="$PROJECT_DIR/setup.log"
ENV_FILE="$PROJECT_DIR/.env"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

# Check if Python is installed
if ! command_exists python3; then
    echo "Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
if [[ "$PYTHON_VERSION" > "$REQUIRED_PYTHON_VERSION" ]]; then
    echo "Python version $REQUIRED_PYTHON_VERSION or higher is required. Installed version: $PYTHON_VERSION."
    exit 1
fi

# Check if systemd is available
if ! command_exists systemctl; then
    echo "systemd is not available. Please ensure you are using a system with systemd."
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory $PROJECT_DIR does not exist. Please ensure the path is correct."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found in $PROJECT_DIR. Please ensure it exists."
    exit 1
fi

# Check for existing virtual environment and prompt for deletion
if [ -d "$VENV_DIR" ]; then
    read -p "Virtual environment already exists. Do you want to delete and recreate it? (y/n): " -r REPLY
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf $VENV_DIR
    else
        echo "Exiting setup."
        exit 1
    fi
fi

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR

# Activate the virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt

# Source environment variables if .env file exists
if [ -f "$ENV_FILE" ]; then
    echo "Sourcing environment variables from $ENV_FILE..."
    # shellcheck disable=SC2046
    export $(grep -v '^#' $ENV_FILE | xargs)
fi

# Backup existing service file
if [ -f "$SERVICE_FILE" ]; then
    echo "Backing up existing service file..."
    mv $SERVICE_FILE $SERVICE_FILE.bak
fi

# Create a systemd service file
echo "Creating systemd service file..."
tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=HomeOps API
After=network.target

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
EnvironmentFile=$PROJECT_DIR/.env
Restart=always

[Install]
WantedBy=multi-user.target

EOL

# Reload systemd to recognize the new service
echo "Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
echo "Enabling and starting the service..."
systemctl enable homeops-api.service
systemctl start homeops-api.service

# Check the status of the service
echo "Checking service status..."
if systemctl is-active --quiet homeops-api.service; then
    echo "Service started successfully!"
else
    echo "Failed to start service. Check the logs for more details."
    exit 1
fi

echo "Setup completed successfully!" | tee -a $LOG_FILE
