#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_DIR="/path/to/your/project"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="homeops-api.service"
LOG_FILE="$PROJECT_DIR/update.log"
BACKUP_DIR="$PROJECT_DIR/backups"
BACKUP_FILE="$BACKUP_DIR/$(date +%Y%m%d%H%M%S).tar.gz"
BRANCH="main"
HEALTH_CHECK_URL="http://localhost:8000/"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log messages with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Function to perform health check
health_check() {
    if command_exists curl; then
        log "Performing health check with curl..."
        if curl --fail --silent --max-time 10 $HEALTH_CHECK_URL; then
            log "Health check passed."
        else
            log "Health check failed."
            return 1
        fi
    elif command_exists wget; then
        log "Performing health check with wget..."
        if wget --quiet --spider --timeout=10 $HEALTH_CHECK_URL; then
            log "Health check passed."
        else
            log "Health check failed."
            return 1
        fi
    else
        log "Neither curl nor wget is installed. Skipping health check."
    fi
}

# Pre-update hook
pre_update() {
    log "Running pre-update tasks..."

    # Notify users of downtime (example)
    log "Notifying users of upcoming downtime..."
    # You can replace this with actual notification logic, e.g., sending an email or a Slack message

    # Run tests (example)
    log "Running pre-update tests..."
    source $VENV_DIR/bin/activate
    if ! pytest; then
        log "Tests failed. Aborting update."
        exit 1
    fi
}

# Post-update hook
post_update() {
    log "Running post-update tasks..."

    # Warm-up application
    log "Warming up the application..."
    if command_exists curl; then
        curl --silent $HEALTH_CHECK_URL > /dev/null
    elif command_exists wget; then
        wget --quiet --spider $HEALTH_CHECK_URL
    fi

    # Send notification of completion (example)
    log "Notifying users of update completion..."
    # You can replace this with actual notification logic, e.g., sending an email or a Slack message
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    log "Please run as root."
    exit 1
fi

# Check if git is installed
if ! command_exists git; then
    log "Git is not installed. Please install Git."
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log "Project directory $PROJECT_DIR does not exist. Please ensure the path is correct."
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR

# Backup current project state
log "Creating backup of current project state..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_FILE" $PROJECT_DIR

# Pre-update tasks
pre_update

# Check for updates
log "Checking for updates on branch $BRANCH..."
if git fetch origin $BRANCH && git diff --quiet origin/$BRANCH; then
    log "No updates available."
    exit 0
else
    log "Pulling latest changes from repository..."
    git pull origin $BRANCH
fi

# Check if requirements.txt exists
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    log "requirements.txt not found in $PROJECT_DIR. Please ensure it exists."
    exit 1
fi

# Activate the virtual environment and install dependencies
log "Activating virtual environment and installing dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt

# Graceful shutdown of the service
log "Stopping the systemd service gracefully..."
systemctl stop $SERVICE_NAME

# Start the systemd service
log "Starting the systemd service..."
systemctl start $SERVICE_NAME

# Health check
if ! health_check; then
    log "Health check failed. Reverting to previous state..."
    tar -xzf "$BACKUP_FILE" -C /
    systemctl restart $SERVICE_NAME
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "Rollback successful. Service is running with the previous state."
    else
        log "Rollback failed. Manual intervention required."
    fi
    exit 1
fi

# Post-update tasks
post_update

# Cleanup old backups (optional)
log "Cleaning up old backups..."
find $BACKUP_DIR -type f -mtime +7 -exec rm {} \;

log "Update completed successfully!"
