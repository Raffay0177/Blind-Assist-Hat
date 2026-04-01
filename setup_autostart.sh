#!/bin/bash

# Ensure script is run with root privileges for systemctl
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (use sudo ./setup_autostart.sh)"
  exit
fi

echo "Setting up auto-start for Blind Assist Hat..."

USER_NAME=$SUDO_USER
if [ -z "$USER_NAME" ]; then
  USER_NAME=$USER
fi

# Set explicit project directory path based on your folder structure
PROJECT_DIR="/home/$USER_NAME/Desktop/BOH/Blind-Assist-Hat"

# Make the start script executable
chmod +x "$PROJECT_DIR/start.sh"

SERVICE_FILE="/etc/systemd/system/blind-assist.service"

echo "Creating systemd service file at $SERVICE_FILE..."

cat > $SERVICE_FILE << EOF
[Unit]
Description=Blind Assist Hat Service
After=network.target sound.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/start.sh
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=blind-assist

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling service to start on boot..."
systemctl enable blind-assist.service

echo "Starting the service now..."
systemctl start blind-assist.service

echo "=========================================================="
echo "Auto-start setup complete! The app should now be running."
echo ""
echo "Helpful commands:"
echo "- Check status: sudo systemctl status blind-assist.service"
echo "- Stop service: sudo systemctl stop blind-assist.service"
echo "- Start service: sudo systemctl start blind-assist.service"
echo "- View logs:    journalctl -u blind-assist.service -f"
echo "=========================================================="
