#!/bin/bash

# Add GPG key for the Fluentd repository
sudo curl -L https://packages.fluentd.org/gpg/fluentd.key | sudo apt-key add -

# Add Fluentd repository to APT sources
echo "deb https://packages.fluentd.org/ubuntu/focal focal main" | sudo tee /etc/apt/sources.list.d/fluentd.list

# Update APT package index
sudo apt update

# Install Fluentd
sudo apt install -y td-agent

# Start Fluentd service
sudo systemctl start td-agent

# Enable Fluentd service to start on boot
sudo systemctl enable td-agent

# Check Fluentd status
sudo systemctl status td-agent
