#!/bin/bash

# Installation of openssh and base64
apt install -y openssh-server

# Create GOTHAM user as an alias for the root account
/usr/sbin/useradd -o -u 0 -g 0 -N -d /root/ -M gotham

# Harden SSH configuration
echo """
# OPENSSH CONFIGURATION POC FOR GOTHAM USE ONLY

Port 22
ListenAddress 0.0.0.0

PermitRootLogin Yes
PubkeyAuthentication yes
""" > /etc/ssh/sshd_config

# Restart openssh
service ssh restart

# Generate a rsa 4096 key pair without passphrase
ssh-keygen -b 4096 -t rsa -f /root/gotham_key -N ""

# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
chmod -R 600 /root/.ssh

# Désactiver le mot de passe
/usr/sbin/usermod -p "default-gotham's-password" gotham

# Show base64 encoded private key user has to send to api
echo "\n\nPrivate key : \n"
/usr/bin/base64 /root/gotham_key | tr -d "\n"
