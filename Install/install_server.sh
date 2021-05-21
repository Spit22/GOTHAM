#!/bin/bash
#
# Authors : GOTHAM Team
# Descr : this script permits to prepare the server environment
#
# Last update : 21/05/2021

set -e pipefail

### DEFINE GLOBAL VARIABLES ###

### DEFINE BINARY PATHS ###
USERADD=$(which useradd)
USERMOD=$(which usermod)
CHMOD=$(which chmod)
KEYGEN=$(which ssh-keygen)
ENCODE=$(which base64)

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo "[-] Please run this script as root"
  exit
fi

### PREPARE GOTHAM SYSTEM ###
echo "=== Preparing the gotham system... ==="

# Create GOTHAM user as an alias for the root account
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1

# Configure password
mdp=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w12 | head -n1)
$USERMOD -p "$mdp" gotham
echo "[+] User gotham created with password : $mdp"

# Create the folder used by GOTHAM servers
mkdir -p /data/tmp
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
echo "[+] All paths created"

### INSTALL RSYSLOG ###
echo "=== Configuring Rsyslog... ==="

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-JSON_template.conf
echo '''
module(load="mmnormalize")

template(name="all-json-template" type="list"){
    property(name="$!all-json")
}

''' > /etc/rsyslog.d/00-JSON_template.conf

# Restart rsyslog
systemctl restart rsyslog
echo "[+] Rsyslog configured"

### INSTALL AND CONFIGURE SSH SERVER ###
echo "=== Installing and configuring SSH... ==="
# Update repository
$APT update > /dev/null 2>&1
echo "[+] APT updated"

# Installation of openssh and base64
$APT install -y openssh-server > /dev/null 2>&1
echo "[+] SSH Server installed"

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
echo "[+] SSH Server configured"

### GENERATE SSH KEY ###
echo "=== Generating SSH Key... ==="

# Generate a rsa 4096 key pair without passphrase
$KEYGEN -b 4096 -t rsa -f /root/gotham_key -N ""

# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
$CHMOD -R 600 /root/.ssh

# Show base64 encoded private key user has to send to api
echo "\n\n[+]Private key generated : \n"
$ENCODE /root/gotham_key | tr -d "\n"
