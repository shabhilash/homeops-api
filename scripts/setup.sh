#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_DIR="${HOMEOPS_DIR}"
PARENT_DIR=$(dirname "$PROJECT_DIR")
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/homeops-api.service"
USER=$(whoami)
REQUIRED_PYTHON_VERSION="3.8"
LOG_FILE="$PARENT_DIR/setup.log"
ENV_FILE="$PROJECT_DIR/.env"
SAMPLE_ENV_FILE="$PROJECT_DIR/.env.sample"
REPO_URL="https://github.com/shabhilash/homeops-api.git"
BRANCH="main"
VERBOSE=0

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log messages with timestamp and log level
log() {
    local level="$1"
    local message="$2"
    if [[ "$level" == "DEBUG" && "$VERBOSE" -eq 0 ]]; then
        return 0
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $level: $message" | tee -a "$LOG_FILE"
}

# Function to log error messages and exit with failure
log_error() {
    log "ERROR" "$1"
    exit 1
}

# Function to log informational messages
log_info() {
    log "INFO" "$1"
}

# Function to log debug messages
log_debug() {
    log "DEBUG" "$1"
}

# Ensure the project directory exists before attempting to write to the log file
if [ ! -d "$PARENT_DIR" ]; then
    log_error "Parent directory $PARENT_DIR does not exist."
fi

# Ensure the log directory exists and create it if necessary
if [ ! -d "$PARENT_DIR" ]; then
    log_debug "Log directory does not exist. Creating directory: $PARENT_DIR"
    sudo mkdir -p "$PARENT_DIR"
    sudo chown "$USER":"$USER" "$PARENT_DIR"
    log_debug "Log directory created: $PARENT_DIR"
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./setup.sh [-v|--verbose] [-h|--help] [-b|--branch BRANCH]"
            echo "Options:"
            echo "  -v, --verbose    Enable verbose logging."
            echo "  -b, --branch     Specify a branch to pull from (default is 'main')."
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            ;;
    esac
done

# Check if HOMEOPS_DIR environment variable is set
if [ -z "$HOMEOPS_DIR" ]; then
    log_error "HOMEOPS_DIR environment variable is not set. Please set it to your project directory."
fi

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root."
fi

# Check if Python is installed
if ! command_exists python3; then
    log_error "Python3 is not installed. Please install Python 3.8 or higher."
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
if [[ "$(printf '%s\n' "$REQUIRED_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_PYTHON_VERSION" ]]; then
    log_error "Python version $REQUIRED_PYTHON_VERSION or higher is required. Installed version: $PYTHON_VERSION."
fi

# Check if systemd is available
if ! command_exists systemctl; then
    log_error "systemd is not available. Please ensure you are using a system with systemd."
fi

# Check if project directory exists or clone the repository
if [ ! -d "$PROJECT_DIR/.git" ]; then
    if [ -d "$PROJECT_DIR" ]; then
        log_info "Project directory exists, but is not a Git repository. Cloning into subdirectory..."
        CLONE_DIR="$PROJECT_DIR/homeops-api"
        git clone "$REPO_URL" "$CLONE_DIR"
    else
        log_info "Project directory does not exist. Cloning the repository..."
        git clone "$REPO_URL" "$PROJECT_DIR"
    fi
else
    log_debug "Project directory already exists. Proceeding with git operations."
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Initialize git if .git folder is missing
if [ ! -d ".git" ]; then
    log_info "Initializing a new Git repository..."
    git init
    git remote add origin "$REPO_URL"
    log_info "Git repository initialized."
fi

# Fetch the latest changes and checkout the desired branch
log_info "Fetching the latest changes from the repository..."
git fetch origin

log_info "Available branches:"
git branch -a | tee -a "$LOG_FILE"

# Check if the branch exists locally or remotely
if git show-ref --quiet refs/heads/"$BRANCH"; then
    log_debug "Branch '$BRANCH' exists locally. Checking out and pulling updates."
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
elif git show-ref --quiet refs/remotes/origin/"$BRANCH"; then
    log_debug "Branch '$BRANCH' exists remotely. Checking out and pulling updates."
    git checkout -b "$BRANCH" origin/"$BRANCH"
else
    log_error "Branch '$BRANCH' does not exist. Please ensure the branch name is correct."
fi

# Check if requirements.txt exists
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    log_error "requirements.txt not found in $PROJECT_DIR. Please ensure it exists."
fi

# Check for existing virtual environment and prompt for deletion
if [ -d "$VENV_DIR" ]; then
    read -p "Virtual environment already exists. Do you want to delete and recreate it? (y/n): " -r REPLY
    if [[ $REPLY =~ ^[Yy][Ee][Ss]?$ ]]; then
        log_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        log_info "Activating virtual environment and installing dependencies..."
        source "$VENV_DIR"/bin/activate
        pip install --upgrade pip
        pip install -r "$PROJECT_DIR"/requirements.txt
    else
        log_info "Updating existing virtual environment..."
        source "$VENV_DIR"/bin/activate
        pip install --upgrade pip
        pip install -r "$PROJECT_DIR"/requirements.txt
    fi
else
    log_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    log_info "Activating virtual environment and installing dependencies..."
    source "$VENV_DIR"/bin/activate
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR"/requirements.txt
fi

# Create .env file if .env.sample exists
if [ -f "$SAMPLE_ENV_FILE" ]; then
    log_info "Copying .env.sample to .env..."
    cp "$SAMPLE_ENV_FILE" "$ENV_FILE"
else
    log_info ".env.sample not found. Please create a .env file manually."
fi

# Backup existing service file
if [ -f "$SERVICE_FILE" ]; then
    log_info "Backing up existing service file..."
    mv $SERVICE_FILE $SERVICE_FILE.bak
fi

# Create a systemd service file
log_info "Creating systemd service file..."
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
log_info "Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
log_info "Enabling and starting the service..."
systemctl enable homeops-api.service
systemctl start homeops-api.service

# Check the status of the service
log_info "Checking service status..."
if systemctl is-active --quiet homeops-api.service; then
    log_info "Service started successfully!"
else
    log_error "Failed to start service. Check the logs for more details."
fi

log_info "Setup completed successfully!"
