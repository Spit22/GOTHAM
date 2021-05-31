#!/bin/bash
#
# Authors : GOTHAM Team
# Descr : this script permits to prepare te orchestrator system and install GOTHAM
#
# Last update : 31/05/2021

set -e pipefail

### DEFINE GLOBAL VARIABLES ###
GOTHAM_HOME=/opt/GOTHAM/
GOTHAM_GIT="https://github.com/Spit22/GOTHAM"
EXEC_BRANCH="dev_v1"

### DEFINE BINARY PATHS ###
USERADD=$(which useradd)
GIT=$(which git)
CHOWN=$(which chown)
CHMOD=$(which chmod)
APT=$(which apt)
RM=$(which rm)

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo "[-] Please run this script as root"
  exit
fi

### PREPARE GOTHAM SYSTEM ###
echo "=== Preparing the gotham system... ==="

# Create GOTHAM user as an alias for the root account
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1
echo "[+] User gotham created"

# Generate the GOTHAM profile
echo -e "#GOTHAM global variables\nexport GOTHAM_HOME=$GOTHAM_HOME" > /etc/profile.d/gotham.sh
$CHMOD +x /etc/profile.d/gotham.sh
echo "[+] Gotham profile generated under /etc/profile.d/gotham.sh"

# Create some paths used by GOTHAM
mkdir -p /data/template
mkdir -p /data/rsyslog/datacenter-configuration
mkdir -p /data/rsyslog/servers-configuration
mkdir -p /data/honeypot-log
mkdir -p /data/link-log
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
echo "[+] All paths created"


### INSTALL DEPENDANCIES ###
echo "=== Installing dependancies... ==="

# Update repository
$APT update > /dev/null 2>&1
echo "[+] APT updated"

# Install needed packages
$APT install -y python3 python3-pip git mariadb-server git > /dev/null 2>&1
PIP3=$(which pip3)
echo "[+] Some packages correctly installed"

# Install libs
$APT install -y libmariadb-dev > /dev/null 2>&1
echo "[+] Some libraries correctly installed"

### INSTALL RSYSLOG ###
echo "=== Configuring Rsyslog... ==="

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-syslog_server.conf
echo '''
$template RawFormat,"%msg%\n"
module(load="imtcp")
input(type="imtcp" port="1514")
''' > /etc/rsyslog.d/00-syslog_server.conf

# Restart rsyslog
systemctl restart rsyslog > /dev/null 2>&1
echo "[+] Rsyslog configured under /etc/rsyslog.d/"


### INSTALL GOTHAM ###
echo "=== Installing GOTHAM... ==="

# Clone repository on this directory
$RM -r $GOTHAM_HOME
$GIT clone $GOTHAM_GIT $GOTHAM_HOME > /dev/null 2>&1
$CHOWN -R gotham:root $GOTHAM_HOME
echo "[+] GOTHAM cloned under $GOTHAM_HOME"

# Going on the repository folder
cd $GOTHAM_HOME

# Choose the git branch
$GIT checkout $EXEC_BRANCH > /dev/null 2>&1
echo "[+] Switched to $EXEC_BRANCH"

# Install all python libs
$PIP3 install -r $GOTHAM_HOME/Orchestrator/Sources/requirements.txt > /dev/null 2>&1
echo "[+] Pip dependancies installed"

# Create the log folder
mkdir -p $GOTHAM_HOME/Orchestrator/Logs

# Configure database
mysql -u root -e "CREATE DATABASE GOTHAM;" > /dev/null 2>&1
mysql -u root GOTHAM < $GOTHAM_HOME/Orchestrator/Internal_Database/gotham.sql > /dev/null 2>&1
echo "[+] MySQL db successfully imported"
