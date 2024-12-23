#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_DIR="${HOMEOPS_DIR}"
PARENT_DIR=$(dirname "$PROJECT_DIR")  # Parent directory
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/homeops-api.service"
USER=$(whoami)

# Function to log messages with timestamp and log level
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to log error messages and exit with failure
log_error() {
    log "ERROR: $1"
    exit 1
}

# Function to log informational messages
log_info() {
    log "INFO: $1"
}

# Check if the HOMEOPS_DIR is set and exists
if [ -z "$HOMEOPS_DIR" ]; then
    log_error "HOMEOPS_DIR environment variable is not set. Please set it to your project directory."
fi

if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory $PROJECT_DIR does not exist."
fi

# Stop and disable the service
log_info "Stopping the service..."
systemctl stop homeops-api.service
log_info "Disabling the service..."
systemctl disable homeops-api.service

# Remove the systemd service file
if [ -f "$SERVICE_FILE" ]; then
    log_info "Removing systemd service file..."
    rm -f "$SERVICE_FILE"
else
    log_info "Systemd service file does not exist."
fi

# Remove the virtual environment
if [ -d "$VENV_DIR" ]; then
    log_info "Removing virtual environment..."
    rm -rf "$VENV_DIR"
else
    log_info "Virtual environment does not exist."
fi

# Optionally, delete the project directory
read -p "Do you want to delete the project directory $PROJECT_DIR? (y/n): " -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Deleting project directory..."
    rm -rf "$PROJECT_DIR"
else
    log_info "Project directory not deleted."
fi

log_info "Uninstallation completed successfully."
