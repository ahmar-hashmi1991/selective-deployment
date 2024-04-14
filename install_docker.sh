#!/bin/bash

echo "1"

# Update package information (Ubuntu/Debian example)
apt-get update
echo "2"

# Install required packages
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
echo "3"

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo "4"

# Set up the stable repository
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
echo "5"

# Install Docker CE
apt-get update
apt-get install -y docker.io
echo "6"

# Add current user to the docker group
usermod -aG docker $USER
echo "7"
