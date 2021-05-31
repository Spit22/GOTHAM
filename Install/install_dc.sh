#!/bin/bash
#
# Authors : GOTHAM Team
# Descr : this script permits to prepare te orchestrator system and install GOTHAM
#
# Last update : 31/05/2021
set -e pipefail

### DEFINE GLOBAL VARIABLES ###

### DEFINE BINARY PATHS ###
USERADD=$(which useradd)
GIT=$(which git)
CHOWN=$(which chown)
CHMOD=$(which chmod)
APT=$(which apt)
APTKEY=$(which apt-key)
KEYGEN=$(which ssh-keygen)
ENCODE=$(which base64)

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo "[-] Please run this script as root"
  exit
fi

# Update repo
$APT update

# Install utils
$APT install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
CURL=$(which curl)

# Add docker's GPG key
$CURL -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -

# Check we have the correct key fingerprint
$APTKEY fingerprint 0EBFCD88 | grep "docker@docker.com"
if [ $? != 0 ]; then
	echo "Key is not valid"
	exit
fi

# Add repository
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

# Install docker
$APT install -y docker-ce docker-ce-cli containerd.io docker-compose
DOCKER=$(which docker)

# Test docker
$DOCKER run hello-world

# Create the folder used by GOTHAM
mkdir -p /data/tmp
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d

# Installation of openssh and base64
$APT install -y openssh-server

# Create GOTHAM user as an alias for the root account
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-JSON_template.conf
echo '''
module(load="mmnormalize")

template(name="all-json-template" type="list"){
    property(name="$!all-json")
}

template(name="default-template" type="list") {
    constant(value="{")
        constant(value="\"timestamp\":\"")     property(name="timereported" dateFormat="rfc3339")
        constant(value="\",\"host\":\"")        property(name="hostname")
        constant(value="\",\"severity\":\"")    property(name="syslogseverity-text")
        constant(value="\",\"tag\":\"")   property(name="syslogtag" format="json")
        constant(value="\",\"message\":\"")    property(name="msg" format="json")
    constant(value="\"}")
}

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
systemctl restart ssh

# Generate a rsa 4096 key pair without passphrase
$KEYGEN -b 4096 -t rsa -f /root/gotham_key -N ""

# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
$CHMOD -R 600 /root/.ssh

# Désactiver le mot de passe
$USERMOD -p "default-gotham's-password" gotham

# Restart again ssh
/usr/sbin/service ssh restart

# Show base64 encoded private key user has to send to api
echo "\n\nPrivate key : \n"
$ENCODE /root/gotham_key | tr -d "\n"
