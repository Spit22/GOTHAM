#!/bin/bash
#
# Authors : GOTHAM Team
# Descr : this script permits to prepare te orchestrator system and install GOTHAM
#
# Last update : 06/04/2022

set -euo pipefail

### COLOR CODES ###
red="\e[0;91m"
blue="\e[0;94m"
green="\e[0;92m"
default="\e[0m"

### DEFINE GLOBAL VARIABLES ###
GOTHAM_HOME=/opt/GOTHAM/
GOTHAM_GIT="https://github.com/Spit22/GOTHAM"
EXEC_BRANCH="remotes/origin/dev_V1"

### DEFINE BINARY PATHS ###
USERADD=$(which useradd) || echo "${red}[-] Unknown command : useradd${default}" && exit 1
CHOWN=$(which chown) || echo "${red}[-] Unknown command : chown${default}" && exit 1
CHMOD=$(which chmod) || echo "${red}[-] Unknown command : chmod${default}" && exit 1
APT=$(which apt) || echo "${red}[-] Unknown command : apt${default}" && exit 1
RM=$(which rm) || echo "${red}[-] Unknown command : rm${default}" && exit 1

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo "${red}[-] Please run this script as root${default}"
  exit 1
fi

### PREPARE GOTHAM SYSTEM ###
echo "${blue}=== Preparing the gotham system... ===${default}"

# Create GOTHAM user as an alias for the root account
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1
echo "${green}[+] User gotham created${default}"

# Generate the GOTHAM profile
echo -e "#GOTHAM global variables\nexport GOTHAM_HOME=$GOTHAM_HOME" > /etc/profile.d/gotham.sh
$CHMOD +x /etc/profile.d/gotham.sh
echo "${green}[+] Gotham profile generated under /etc/profile.d/gotham.sh${default}"

# Create some paths used by GOTHAM
mkdir -p /data/template
mkdir -p /data/rsyslog/datacenter-configuration
mkdir -p /data/rsyslog/servers-configuration
mkdir -p /data/honeypot-log
mkdir -p /data/link-log
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
echo "${green}[+] All paths created${default}"


### INSTALL DEPENDANCIES ###
echo "${blue}=== Installing dependancies... ===${default}"

# Update repository
$APT update > /dev/null 2>&1
echo "${green}[+] APT updated${default}"

# Install needed packages
$APT install -y python3 python3-pip git mariadb-server git rsyslog > /dev/null 2>&1
PIP3=$(which pip3)
GIT=$(which git)
echo "${green}[+] Some packages correctly installed${default}"

# Install libs
$APT install -y libmariadb-dev > /dev/null 2>&1
echo "${green}[+] Some libraries correctly installed${default}"

### INSTALL RSYSLOG ###
echo "${blue}=== Configuring Rsyslog... ===${default}"

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-syslog_server.conf
echo '''
$template RawFormat,"%msg%\n"
module(load="imtcp")
input(type="imtcp" port="1514")
''' > /etc/rsyslog.d/00-syslog_server.conf

# Restart rsyslog
systemctl restart rsyslog > /dev/null 2>&1
echo "${green}[+] Rsyslog configured under /etc/rsyslog.d/${default}"


### INSTALL GOTHAM ###
echo "${blue}=== Installing GOTHAM... ===${default}"

# Clone repository on this directory
$GIT clone $GOTHAM_GIT $GOTHAM_HOME > /dev/null 2>&1
$CHOWN -R gotham:root $GOTHAM_HOME
echo "${green}[+] GOTHAM cloned under $GOTHAM_HOME${default}"

# Going on the repository folder
cd $GOTHAM_HOME

# Choose the git branch
$GIT checkout $EXEC_BRANCH > /dev/null 2>&1
echo "${green}[+] Switched to $EXEC_BRANCH${default}"

# Install all python libs
$PIP3 install -r $GOTHAM_HOME/Orchestrator/Sources/requirements.txt > /dev/null 2>&1
echo "${green}[+] Pip dependancies installed${default}"

# Create the log folder
mkdir -p $GOTHAM_HOME/Orchestrator/Logs

# Configure database
mysql -u root -e "CREATE DATABASE GOTHAM;" > /dev/null 2>&1
mysql -u root GOTHAM < $GOTHAM_HOME/Orchestrator/Internal_Database/gotham.sql > /dev/null 2>&1
echo "${green}[+] MySQL db successfully imported${default}"
