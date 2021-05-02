#!/bin/bash

# Update repo
apt-get update

# Install utils
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

# Add docker's GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -

# Check we have the correct key fingerprint
apt-key fingerprint 0EBFCD88 | grep "docker@docker.com"
if [ $? != 0 ]; then
	echo "Key is not valid"
	exit
fi

# Add repository
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

# Update repo again
apt-get update

# Install docker
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose

# Test docker
docker run hello-world

# Create the folder used by GOTHAM
mkdir -p /data/tmp
mkdir -p /data/rsyslog/rulebase

# Installation of openssh and base64
apt install -y openssh-server

# Create GOTHAM user as an alias for the root account
/usr/sbin/useradd -o -u 0 -g 0 -N -d /root/ -M gotham

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-JSON_template.conf
echo '''
template(name="JSON_template" type="list"){property(name="$!all-json")}
''' > /etc/rsyslog.d/00-JSON_template.conf

# Restart rsyslog
systemctl restart rsyslog

# Harden SSH configuration
echo """
# OPENSSH CONFIGURATION POC FOR GOTHAM USE ONLY

Port 22
ListenAddress 0.0.0.0

PermitRootLogin Yes
PubkeyAuthentication yes
""" > /etc/ssh/sshd_config

# Restart openssh
/usr/sbin/service ssh restart

# Generate a rsa 4096 key pair without passphrase
ssh-keygen -b 4096 -t rsa -f /root/gotham_key -N ""

# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
chmod -R 600 /root/.ssh

# Désactiver le mot de passe
usermod -p "default-gotham's-password" gotham

# Restart again ssh
/usr/sbin/service ssh restart

# Show base64 encoded private key user has to send to api
echo "\n\nPrivate key : \n"
/usr/bin/base64 /root/gotham_key | tr -d "\n"
