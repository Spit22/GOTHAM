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

### COLOR CODES ###
red="\e[0;91m"
blue="\e[0;94m"
green="\e[0;92m"
yellow="\e[0;33m"
default="\e[0m"

### DEFINE GLOBAL VARIABLES ###
GOTHAM_HOME=/opt/GOTHAM/
GOTHAM_GIT="https://github.com/Spit22/GOTHAM"
EXEC_BRANCH="remotes/origin/dev_V1"

### DEFINE BINARY PATHS ###
USERADD=$(which useradd) || (echo -e "${red}[-] Unknown command : useradd${default}" && exit 1)
CHOWN=$(which chown) || (echo -e "${red}[-] Unknown command : chown${default}" && exit 1)
CHMOD=$(which chmod) || (echo -e "${red}[-] Unknown command : chmod${default}" && exit 1)
APT=$(which apt) || (echo -e "${red}[-] Unknown command : apt${default}" && exit 1)
RM=$(which rm) || (echo -e "${red}[-] Unknown command : rm${default}" && exit 1)

### CHECK IF ROOT ###
if [ "$EUID" -ne 0 ]
  then echo -e "${red}[-] Please run this script as root${default}"
  exit 1
fi

### PREPARE GOTHAM SYSTEM ###
echo -e "${blue}=== Prepare the gotham system ===${default}"

# Create GOTHAM user as an alias for the root account
echo -ne "${yellow}[...] Creating gotham user${default}"
$USERADD -o -u 0 -g 0 -N -d /root/ -M gotham > /dev/null 2>&1  || (echo -ne "${red}\n[-] Error creating gotham user\n${default}" && exit 1)
echo -ne "${green}\r[+] gotham user created\n${default}"

# Generate the GOTHAM profile
echo -ne "${yellow}[...] Generating GOTHAM profile${default}"
echo -e "#GOTHAM global variables\nexport GOTHAM_HOME=$GOTHAM_HOME" > /etc/profile.d/gotham.sh
$CHMOD +x /etc/profile.d/gotham.sh || (echo -ne "${red}\n[-] Error generating gotham profile\n${default}" && exit 1)
echo -ne "${green}\r[+] Gotham profile generated under /etc/profile.d/gotham.sh\n${default}"

# Create some paths used by GOTHAM
mkdir -p /data/template
mkdir -p /data/rsyslog/datacenter-configuration
mkdir -p /data/rsyslog/servers-configuration
mkdir -p /data/honeypot-log
mkdir -p /data/link-log
mkdir -p /data/rsyslog/rulebase
mkdir -p /etc/rsyslog.d
echo -e "${green}[+] All paths created${default}"


### INSTALL DEPENDANCIES ###
echo -e "${blue}=== Install dependancies ===${default}"

# Update repository
echo -ne "${yellow}[...] Updating system${default}"
$APT update > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error updating system\n${default}" && exit 1)
echo -ne "${green}\r[+] System updated\n${default}"

# Install needed packages
echo -ne "${yellow}[...] Installing packages${default}"
$APT install -y python3 python3-pip git mariadb-server git rsyslog > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing packages\n${default}" && exit 1)
PIP3=$(which pip3)
GIT=$(which git)
echo -ne "${green}\r[+] Packages correctly installed\n${default}"

# Install libs
echo -ne "${yellow}[...] Installing libraries${default}"
$APT install -y libmariadb-dev > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing libraries\n${default}" && exit 1)
echo -ne "${green}\r[+] Libraries correctly installed\n${default}"

### INSTALL RSYSLOG ###
echo -e "${blue}=== Configure Rsyslog ===${default}"

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-syslog_server.conf
echo '''
$template RawFormat,"%msg%\n"
module(load="imtcp")
input(type="imtcp" port="1514")
''' > /etc/rsyslog.d/00-syslog_server.conf

# Restart rsyslog
echo -ne "${yellow}[...] Configuring rsyslog${default}"
systemctl restart rsyslog > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error restarting rsyslog\n${default}" && exit 1)
echo -ne "${green}\r[+] Rsyslog configured under /etc/rsyslog.d/\n${default}"


### INSTALL GOTHAM ###
echo -e "${blue}=== Install GOTHAM ===${default}"

# Clone repository on this directory
echo -ne "${yellow}[...] Cloning GOTHAM repository${default}"
$GIT clone $GOTHAM_GIT $GOTHAM_HOME > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error cloning GOTHAM repository in /opt\n${default}" && exit 1)
$CHOWN -R gotham:root $GOTHAM_HOME || (echo -ne "${red}\n[-] Error setting owner of GOTHAM repository\n${default}" && exit 1)
echo -ne "${green}\r[+] GOTHAM cloned under $GOTHAM_HOME\n${default}"

# Going on the repository folder
cd $GOTHAM_HOME

# Choose the git branch
$GIT checkout $EXEC_BRANCH > /dev/null 2>&1
echo -e "${green}[+] Switched to $EXEC_BRANCH${default}"

# Install all python libs
echo -ne "${yellow}[...] Installing python dependancies${default}"
$PIP3 install -r $GOTHAM_HOME/Orchestrator/Sources/requirements.txt > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error installing python dependancies\n${default}" && exit 1)
echo -ne "${green}\r[+] Python dependancies installed\n${default}"

# Create the log folder
mkdir -p $GOTHAM_HOME/Orchestrator/Logs

# Configure database
echo -ne "${yellow}[...] Creating database${default}"
mysql -u root -e "CREATE DATABASE GOTHAM;" > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error creating gotham's database\n${default}" && exit 1)
mysql -u root GOTHAM < $GOTHAM_HOME/Orchestrator/Internal_Database/gotham.sql > /dev/null 2>&1 || (echo -ne "${red}\n[-] Error importing gotham's database\n${default}" && exit 1)
echo -ne "${green}\r[+] MySQL db successfully imported\n${default}"
