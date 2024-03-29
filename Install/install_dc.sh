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
USERMOD=$(which usermod)
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

### PREPARE GOTHAM SYSTEM ###
echo "=== Preparing the gotham system... ==="

# Create GOTHAM user as an alias for the root account
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1

# Configure password
mdp=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w50 | head -n1)
$USERMOD -p "$mdp" gotham
echo "[+] User gotham created with password : $mdp"

# Create the folder used by GOTHAM
mkdir -p /data/tmp
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
mkdir -p /etc/rsyslog.d
echo "[+] All paths created"

### INSTALL DEPENDANCIES ###
echo "=== Installing dependancies... ==="

# Update repo
$APT update > /dev/null 2>&1
echo "[+] APT updated"

# Install utils
$APT install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    gnupg-agent \
    rsyslog \
    software-properties-common > /dev/null 2>&1
CURL=$(which curl)
GIT=$(which git)
echo "[+] Some packages successfully installed"

# Add docker's GPG key
$CURL -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - > /dev/null 2>&1
echo "[+] Docker apt key configured"

# Check we have the correct key fingerprint
$APTKEY fingerprint 0EBFCD88 | grep "docker@docker.com" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "Key is not valid"
	exit
fi

# Add repository
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable" > /dev/null 2>&1

# Update repo again
$APT update > /dev/null 2>&1
# Install docker
$APT install -y docker-ce docker-ce-cli containerd.io docker-compose > /dev/null 2>&1
DOCKER=$(which docker)

# Test docker
$DOCKER run hello-world > /dev/null 2>&1
echo "[+] Docker successfully installed"

### INSTALL RSYSLOG ###
echo "=== Configuring Rsyslog... ==="

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-JSON_template.conf
echo '''
module(load="mmnormalize")

template(name="all-json-template" type="list"){
    constant(value="{")
    constant(value="\"tag\":\"")   property(name="programname" format="json")
    constant(value="\",")
    property(name="$!all-json" position.from="2")
}

template(name="default-template" type="list") {
    constant(value="{")
        constant(value="\"timestamp\":\"")     property(name="timereported" dateFormat="rfc3339")
        constant(value="\",\"host\":\"")        property(name="hostname")
        constant(value="\",\"severity\":\"")    property(name="syslogseverity-text")
        constant(value="\",\"tag\":\"")   property(name="programname" format="json")
        constant(value="\",\"message\":\"")    property(name="msg" format="json")
    constant(value="\"}")
}

''' > /etc/rsyslog.d/00-JSON_template.conf

# Restart rsyslog
systemctl restart rsyslog > /dev/null 2>&1
echo "[+] Rsyslog configured"

### INSTALL AND CONFIGURE SSH SERVER ###
echo "=== Installing and configuring SSH... ==="

# Update repo
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
systemctl restart ssh > /dev/null 2>&1
echo "[+] SSH Server configured"

### GENERATE SSH KEY ###
echo "=== Generating SSH Key... ==="

# Generate a rsa 4096 key pair without passphrase
$KEYGEN -b 4096 -t rsa -f /root/gotham_key -N "" > /dev/null 2>&1

# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
$CHMOD -R 600 /root/.ssh

# Restart again ssh
/usr/sbin/service ssh restart > /dev/null 2>&1

# Show base64 encoded private key user has to send to api
echo -e "\n\n[+]Private key : \n"
$ENCODE /root/gotham_key | tr -d "\n"
echo ""
