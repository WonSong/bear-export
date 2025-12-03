#!/bin/bash

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_SCRIPT="$SCRIPT_DIR/export.py"
PYTHON_BIN=$(which python3)
PLIST_LABEL="com.bearexport.scheduler"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
LOG_PATH="$SCRIPT_DIR/export.log"

# Function to create the LaunchAgent plist file
create_plist() {
    mkdir -p "$HOME/Library/LaunchAgents"
    
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_BIN</string>
        <string>$EXPORT_SCRIPT</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>StartInterval</key>
    <integer>30</integer>
    <key>StandardOutPath</key>
    <string>$LOG_PATH</string>
    <key>StandardErrorPath</key>
    <string>$LOG_PATH</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF
}

# Function to install the LaunchAgent
install_launcher() {
    create_plist
    launchctl load "$PLIST_PATH"
    
    echo "✓ LaunchAgent installed successfully"
    echo "Bear notes will be exported every 30 seconds"
    echo "Logs will be written to: $LOG_PATH"
}

# Function to uninstall the LaunchAgent
uninstall_launcher() {
    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
        rm "$PLIST_PATH"
        echo "✓ LaunchAgent removed successfully"
    else
        echo "✗ No LaunchAgent found"
    fi
}

# Function to check LaunchAgent status
status_launcher() {
    if [ -f "$PLIST_PATH" ]; then
        if launchctl list | grep -q "$PLIST_LABEL"; then
            echo "✓ LaunchAgent is active and loaded"
            echo "Plist: $PLIST_PATH"
        else
            echo "⚠ LaunchAgent plist exists but is not loaded"
            echo "Run './schedule.sh start' to load it"
        fi
    else
        echo "✗ No LaunchAgent found"
    fi
}

# Main script logic
case "$1" in
    start)
        install_launcher
        ;;
    stop)
        uninstall_launcher
        ;;
    status)
        status_launcher
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        echo "  start  - Install LaunchAgent to export Bear notes every 30 seconds"
        echo "  stop   - Remove the LaunchAgent"
        echo "  status - Check if LaunchAgent is running"
        exit 1
        ;;
esac
