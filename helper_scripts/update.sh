#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_DIR="$HOMEOPS_DIR"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="homeops-api.service"
LOG_FILE="$PROJECT_DIR/update.log"
BACKUP_DIR="/tmp/backups"
BACKUP_FILE="$BACKUP_DIR/$(date +%Y%m%d%H%M%S).tar.gz"
BRANCH="main"
HEALTH_CHECK_URL="http://localhost:8000/"
VERBOSE=0
NO_BACKUP=0  # Default: Backup is taken
SKIP_TESTS=0  # Default: Tests are run


# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


# Function to log messages with timestamp and log level
log() {
    local level="$1"
    local message="$2"
    if [[ "$level" == "DEBUG" && "$VERBOSE" -eq 0 ]]; then
        return 0  # Do nothing if not verbose
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $level: $message" | tee -a "$LOG_FILE"
}

# Function to log error messages and exit with failure
log_error() {
    log "ERROR" "$1"
    exit 1

}

# Function to perform health check
health_check() {
    if command_exists curl; then
        log "INFO" "Performing health check with curl..."
        if ! curl --fail --silent --max-time 10 "$HEALTH_CHECK_URL"; then
            log_error "Health check failed using curl."
        else
            log "INFO" "Health check passed."
        fi
    elif command_exists wget; then
        log "INFO" "Performing health check with wget..."
        if ! wget --quiet --spider --timeout=10 "$HEALTH_CHECK_URL"; then
            log_error "Health check failed using wget."
        else
            log "INFO" "Health check passed."
        fi
    else
        log_error "Neither curl nor wget is installed. Cannot perform health check."
    fi
}

# Pre-update hook
pre_update() {
    log "INFO" "Running pre-update tasks..."
    if [ "$SKIP_TESTS" -eq 0 ]; then
        log "INFO" "Running pre-update tests..."
        source "$VENV_DIR/bin/activate"
        if ! pytest; then
            log_error "Pre-update tests failed."
        fi
        log "INFO" "Pre-update tests passed."
    else
        log "INFO" "Skipping pre-update tests as per --skip-tests option."
    fi
}

# Post-update hook
post_update() {
    log "INFO" "Running post-update tasks..."
    log "INFO" "Warming up the application..."
    if command_exists curl; then
        if ! curl --silent "$HEALTH_CHECK_URL" > /dev/null; then
            log_error "Post-update warm-up failed using curl."
        fi
    elif command_exists wget; then
        if ! wget --quiet --spider "$HEALTH_CHECK_URL"; then
            log_error "Post-update warm-up failed using wget."
        fi
    else
        log_error "Neither curl nor wget is available for post-update warm-up."
    fi
    log "INFO" "Post-update warm-up completed."
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            echo "Usage: HOMEOPS_DIR=/path/to/your/project ./update.sh [-v|--verbose] [-h|--help] [--no-backup] [--skip-tests]"
            exit 0
            ;;
        --no-backup)
            NO_BACKUP=1
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=1
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            ;;
    esac
done

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root."
fi

# Check if git is installed
if ! command_exists git; then
    log "Git is not installed. Please install Git."
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory $PROJECT_DIR does not exist. Please ensure the path is correct."
fi

# Initialize progress
TOTAL_STEPS=8
CURRENT_STEP=0

# Navigate to project directory
cd "$PROJECT_DIR"
log "INFO" "Navigating to project directory..."

# Backup current project state if --no-backup is not passed
if [ "$NO_BACKUP" -eq 0 ]; then
    log "INFO" "Creating backup of current project state..."
    mkdir -p "$BACKUP_DIR"
    # Use --transform option to avoid leading "/" in the archive
    tar --exclude="$BACKUP_DIR" -czf "$BACKUP_FILE" --transform 's,^/,,' "$PROJECT_DIR" || log_error "Failed to create backup."
    log "INFO" "Backup completed."
else
    log "INFO" "Skipping backup step as per --no-backup option."
fi

# Pre-update tasks
pre_update

# Check for updates
log "INFO" "Checking for updates on branch $BRANCH..."
if git fetch origin "$BRANCH" && git diff --quiet origin/"$BRANCH"; then
    log "INFO" "No updates available."
else
    log "INFO" "Pulling latest changes from repository..."
    git pull origin "$BRANCH" || log_error "Failed to pull updates from the repository."
fi

# Install dependencies
log "INFO" "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt" || log_error "Failed to install dependencies."

# Graceful shutdown of the service
log "INFO" "Stopping the systemd service gracefully..."
systemctl stop "$SERVICE_NAME" || log_error "Failed to stop the service."

# Start the systemd service
log "INFO" "Starting the systemd service..."
systemctl start "$SERVICE_NAME" || log_error "Failed to start the service."

# Health check
if ! health_check; then
    log "ERROR" "Health check failed. Reverting to previous state..."
    tar -xzf "$BACKUP_FILE" -C / || log_error "Failed to restore backup."
    systemctl restart "$SERVICE_NAME" || log_error "Failed to restart the service after restoring the backup."
    exit 1
fi

# Post-update tasks
post_update


# Cleanup old backups (optional)
log "Cleaning up old backups..."
find $BACKUP_DIR -type f -mtime +7 -exec rm {} \;

log "Update completed successfully!"
