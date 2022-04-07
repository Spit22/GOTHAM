#!/bin/bash
#
# Authors : GOTHAM Team
# Descr : this script permits to prepare te orchestrator system and install GOTHAM
#
# Last update : 07/04/2022

# Production mode
set -euo pipefail

# Debug mode
#set -euxo pipefail

### DEFINE GLOBAL VARIABLES ###

### COLOR CODES ###
red="\e[0;91m"
blue="\e[0;94m"
green="\e[0;92m"
yellow="\e[0;33m"
default="\e[0m"

### DEFINE BINARY PATHS ###
USERADD=$(which useradd) || (echo -e "${red}[-] Unknown command : useradd${default}" && exit 1)
USERMOD=$(which usermod) || (echo -e "${red}[-] Unknown command : usermod${default}" && exit 1)
CHOWN=$(which chown) || (echo -e "${red}[-] Unknown command : chown${default}" && exit 1)
CHMOD=$(which chmod) || (echo -e "${red}[-] Unknown command : chmod${default}" && exit 1)
APT=$(which apt) || (echo -e "${red}[-] Unknown command : apt${default}" && exit 1)
APTKEY=$(which apt-key) || (echo -e "${red}[-] Unknown command : apt-key${default}" && exit 1)
KEYGEN=$(which ssh-keygen) || (echo -e "${red}[-] Unknown command : ssh-keygen${default}" && exit 1)
ENCODE=$(which base64) || (echo -e "${red}[-] Unknown command : base64${default}" && exit 1)

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo -e "${red}[-] Please run this script as root${default}"
  exit
fi

### PREPARE GOTHAM SYSTEM ###
echo -e "${blue}=== Prepare the gotham system ===${default}"

# Create GOTHAM user as an alias for the root account
echo -ne "${yellow}[...] Creating gotham user${default}"
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1  || (echo -ne "${red}\n[-] Error creating gotham user\n${default}" && exit 1)
echo -ne "${green}\r[+] gotham user created\n${default}"

# Configure password
echo -ne "${yellow}[...] Configuring gotham's password${default}"
mdp=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w50 | head -n1)
$USERMOD -p "$mdp" gotham || (echo -ne "${red}\n[-] Error configuring gotham's password\n${default}" && exit 1)
echo -ne "${green}\r[+] User gotham created with password : $mdp\n${default}"

# Create the folder used by GOTHAM
mkdir -p /data/tmp
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
mkdir -p /etc/rsyslog.d
echo -e "${green}[+] All paths created${default}"

### INSTALL DEPENDANCIES ###
echo -e "${blue}=== Installing dependancies... ===${default}"

# Update repo
echo -ne "${yellow}[...] Updating system${default}"
$APT update > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error updating system\n${default}" && exit 1)
echo -ne "${green}\r[+] System updated\n${default}"

# Install packages
echo -ne "${yellow}[...] Installing packages${default}"
$APT install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    gnupg-agent \
    rsyslog \
    software-properties-common > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing packages\n${default}" && exit 1)
CURL=$(which curl)
GIT=$(which git)
echo -ne "${green}\r[+] Packages correctly installed\n${default}"

# Add docker's GPG key
echo -ne "${yellow}[...] Installing Docker's GPG key${default}"
$CURL -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing Docker's GPG key\n${default}" && exit 1)
echo -ne "${green}\r[+] Docker GPG key installed\n${default}"

# Check we have the correct key fingerprint
echo -ne "${yellow}[...] Checking Docker's GPG key${default}"
$APTKEY fingerprint 0EBFCD88 | grep "docker@docker.com" > /dev/null 2>&1 || (echo -ne "${red}\n[-] Docker's key is invalid\n${default}" && exit 1)
echo -ne "${green}\r[+] Docker GPG key checked\n${default}"

# Add repository
echo -ne "${yellow}[...] Adding docker apt repository${default}"
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable" > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error adding docker apt repository\n${default}" && exit 1)
echo -ne "${green}\r[+] Docker apt repository added\n${default}"

# Update repo
echo -ne "${yellow}[...] Updating system${default}"
$APT update > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error updating system\n${default}" && exit 1)
echo -ne "${green}\r[+] System updated       \n${default}"

# Install docker
echo -ne "${yellow}[...] Installing docker${default}"
$APT install -y docker-ce docker-ce-cli containerd.io docker-compose > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing docker\n${default}" && exit 1)
DOCKER=$(which docker)
echo -ne "${green}\r[+] Docker installed         \n${default}"

# Test docker
echo -ne "${yellow}[...] Testing docker installation${default}"
$DOCKER run hello-world > /dev/null 2>&1 || (echo -ne "${red}\n[-] Docker failed to run\n${default}" && exit 1)
echo -ne "${green}\r[+] Docker successfully tested         \n${default}"

### INSTALL RSYSLOG ###
echo -e "${blue}=== Configure Rsyslog ===${default}"

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
echo -ne "${yellow}[...] Configuring rsyslog${default}"
systemctl restart rsyslog > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error restarting rsyslog\n${default}" && exit 1)
echo -ne "${green}\r[+] Rsyslog configured under /etc/rsyslog.d/\n${default}"

### INSTALL AND CONFIGURE SSH SERVER ###
echo -e "${blue}=== Install and configure SSH server ===${default}"

# Update repo
echo -ne "${yellow}[...] Updating system${default}"
$APT update > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error updating system\n${default}" && exit 1)
echo -ne "${green}\r[+] System updated       \n${default}"

# Installation of openssh and base64
echo -ne "${yellow}[...] Installing OpenSSH${default}"
$APT install -y openssh-server > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing OpenSSH\n${default}" && exit 1)
echo -ne "${green}\r[+] OpenSSH server installed       \n${default}"

# Harden SSH configuration
echo """
# OPENSSH CONFIGURATION POC FOR GOTHAM USE ONLY

Port 22
ListenAddress 0.0.0.0

PermitRootLogin Yes
PubkeyAuthentication yes
""" > /etc/ssh/sshd_config

# Restart openssh
echo -ne "${yellow}[...] Restarting ssh server${default}"
systemctl restart ssh > /dev/null 2>&1 || (echo -ne "${red}\n[-] ssh server failed to restart\n${default}" && exit 1)
echo -ne "${green}\r[+] ssh server configured       \n${default}"

### GENERATE SSH KEY ###
echo -e "${blue}=== Generate SSH Key ===${default}"

# Generate a rsa 4096 key pair without passphrase
echo -ne "${yellow}[...] Generating SSH key${default}"
$KEYGEN -b 4096 -t rsa -f /root/gotham_key -N "" > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error generating ssh key\n${default}" && exit 1)
echo -ne "${green}\r[+] ssh server configured       \n${default}"


# Copy the public key to authorized keys of root users
mkdir -p /root/.ssh
pubkey=$(cat /root/gotham_key.pub)
echo $pubkey >> /root/.ssh/authorized_keys
$CHMOD -R 600 /root/.ssh

# Restart again ssh
echo -ne "${yellow}[...] Restarting ssh server${default}"
/usr/sbin/service ssh restart > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error restarting ssh server\n${default}" && exit 1)
echo -ne "${green}\r[+] ssh server restarted       \n${default}"

# Show base64 encoded private key user has to send to api
echo -e "\n\n[+]Private key : \n"
$ENCODE /root/gotham_key | tr -d "\n"
echo ""
