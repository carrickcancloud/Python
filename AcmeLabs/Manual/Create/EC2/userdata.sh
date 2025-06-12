#!/bin/bash
# ---------------------------------------------------------------------------------------
# Title: EC2 User Data Script
# Date: 2025-06-12
# Version: 1.1
# Written By: Carrick Bradley
# Tested on: Ubuntu 22.04 LTS (Jammy Jellyfish) & Ubuntu 24.04 (Noble Numbat)
# & Ubuntu 24.10 (Oracular Oriole)
# ---------------------------------------------------------------------------------------
# Description: This script performs the following tasks:
# - Updates and upgrades the operating system
# - Installs Apache web server
# - Configures Apache2 with a custom index.html file
#
# Usage: ./user-data.sh [log_file_path]
# Requirements: This script requires root privileges to run and will run on
#               Ubuntu 22.04 LTS (Jammy Jellyfish) & Ubuntu 24.04 (Noble Numbat)
#               & Ubuntu 24.10 (Oracular Oriole) and other Debian-based systems.
# ---------------------------------------------------------------------------------------

# Exit on error, uninitialized variable, or failed command in a pipeline
set -euo pipefail

# Define exit codes
SUCCESS=0
ERROR=1

# Define the log file variable with a timestamp or use provided path
LOGFILE="${1:-/var/log/startup-script-$(date '+%Y%m%d_%H%M%S').log}"

# Define a lock file variable
LOCKFILE="/var/run/user-data-script.lock"

# Function to log messages with a default log level of INFO
log_capture() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Check if the message has already been logged
    if grep -qF "$message" "$LOGFILE"; then
        return  # Skip logging if the message is already in the log file
    fi

    echo "$timestamp - [$level] - $message" | tee -a "$LOGFILE"
    logger -t startup-script "$message"
}

# Function to initialize logging
initialize_logging() {
    log_capture "Initializing logging to '$LOGFILE'..."
    
    # Create log file if it does not exist
    if [ ! -f "$LOGFILE" ]; then
        touch "$LOGFILE"
        log_capture "Log file '$LOGFILE' created."
    else
        log_capture "Log file '$LOGFILE' already exists...appending to it."
    fi

    exec > >(tee -a "$LOGFILE") 2>&1
    log_capture "Logging initialized."
    log_capture "Starting EC2 user data script..."
}

# Function to check if the script is already running
check_running() {
    if [ -f "$LOCKFILE" ]; then
        log_capture "User data script is already running. Exiting."
        exit $SUCCESS
    fi
    touch "$LOCKFILE"
}

# Function to update & upgrade the operating system
update_and_upgrade_os() {
    log_capture "Updating package list..."
    if ! apt-get update -y; then
        log_capture "Error: Failed to update package list." "ERROR"
        exit $ERROR
    fi
    log_capture "Package list updated successfully."

    log_capture "Upgrading installed packages..."
    if ! apt-get upgrade -y; then
        log_capture "Error: Failed to upgrade packages." "ERROR"
        exit $ERROR
    fi
    log_capture "Packages upgraded successfully."

    log_capture "Removing unnecessary packages..."
    if ! apt-get autoremove -y; then
        log_capture "Error: Failed to remove unnecessary packages." "ERROR"
        exit $ERROR
    fi
    log_capture "Unnecessary packages removed successfully."

    log_capture "Cleaning up package files..."
    if ! apt-get autoclean -y; then
        log_capture "Error: Failed to clean up package files." "ERROR"
        exit $ERROR
    fi
    log_capture "Package files cleaned up successfully."
}

# Function to install Apache web server
install_apache() {
    log_capture "Installing Apache web server..."
    if ! apt-get install -y apache2; then
        log_capture "Error: Failed to install Apache web server." "ERROR"
        exit $ERROR
    fi
    log_capture "Apache web server installed successfully."
}

# Function to configure Apache2
configure_apache() {
    log_capture "Configuring Apache web server..."

    # Change to the default Apache2 directory and create index.html
    log_capture "Creating index.html file..."
    if ! cd /var/www/html; then
        log_capture "Error: Failed to change directory to /var/www/html." "ERROR"
        exit $ERROR
    fi
    log_capture "Changed directory to /var/www/html."

    log_capture "Removing existing index.html file..."
    # Remove existing index.html file if it exists
    # 2>/dev/null suppresses error if the file does not exist
    if ! rm -f index.html; then
        log_capture "Error: Failed to remove existing index.html file." "ERROR"
        exit $ERROR
    fi
    log_capture "Existing index.html file removed successfully."

    log_capture "Creating new index.html file..."
    # Create a new index.html file with a welcome message
    cat <<EOF > index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to LUIT</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a0f4b, #000000);
            color: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            overflow: hidden;
        }
        h1 {
            font-size: 4em;
            color: #ff4081;
            animation: futuristicEffect 1.5s infinite alternate;
        }
        h2 {
            font-size: 3em;
            color: #39ff14;
            animation: futuristicEffect 1.5s infinite alternate;
        }
        @keyframes futuristicEffect {
            0% { transform: scale(1); }
            100% { transform: scale(1.05); }
        }
        .button {
            margin-top: 30px;
            padding: 15px 30px;
            font-size: 1.5em;
            color: #ffffff;
            background-color: #ff4081;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #d5006d;
        }
    </style>
</head>
<body>
    <div>
        <h1>Welcome to LUIT</h1>
        <h2>Green Team - DevOps - February 2025</h2>
        <button class="button" onclick="window.location.href='https://levelupintech.com'">Get Started</button>
    </div>
</body>
</html>
EOF

    log_capture "index.html file created successfully."

    # Set permissions for the index.html file
    log_capture "Setting permissions for index.html file..."
    if ! chmod 644 index.html; then
        log_capture "Error: Failed to set permissions for index.html." "ERROR"
        exit $ERROR
    fi
    log_capture "Permissions set successfully."

    # Enable Apache2 service
    log_capture "Enabling Apache2 service..."
    if ! systemctl enable apache2; then
        log_capture "Error: Failed to enable Apache2 service." "ERROR"
        exit $ERROR
    fi
    log_capture "Apache2 service enabled successfully."

    # Start Apache2 service
    log_capture "Starting Apache2 service..."
    if ! systemctl start apache2; then
        log_capture "Error: Failed to start Apache2 service." "ERROR"
        exit $ERROR
    fi
    log_capture "Apache2 service started successfully."
    log_capture "Apache web server configured successfully."
}

# Main execution
initialize_logging
check_running
update_and_upgrade_os
install_apache
configure_apache

# Log the completion of our script
log_capture "Amazon EC2 user data script completed successfully!"
exit $SUCCESS