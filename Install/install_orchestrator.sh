#!/bin/bash

# Update repository
apt update

# Install needed packages
apt install -y python3 python3-pip git mariadb-server

# Install libs
apt install -y libmariadb-dev

# Going to /opt to install GOTHAM
cd /opt

# Clone repository on this directory
git clone https://github.com/Spit22/GOTHAM
chown -R gotham:root $GOTHAM_HOME

# Configure $GOTHAM_HOME var
echo -e "\nexport GOTHAM_HOME=/opt/GOTHAM/" >> /etc/profile
GOTHAM_HOME=/opt/GOTHAM/
source /etc/profile

# Going on the repository folder
cd $GOTHAM_HOME/Orchestrator/Sources

# Choose the git branch
git checkout dev_V1_1


# Install all python libs
pip3 install -r requirements.txt

# Create /data to store GTOAHM's data
mkdir -p $GOTHAM_HOME/Orchestrator/Logs
mkdir -p /data/template
mkdir -p /data/rsyslog/datacenter-configuration
mkdir -p /data/honeypot-log
mkdir -p /data/rsyslog/rulebase

# Pre-configure rsyslog
touch /etc/rsyslog.d/00-syslog_server.conf
echo '''
module(load="imtcp")
input(type="imtcp" port="1514")
''' > /etc/rsyslog.d/00-syslog_server.conf

# Restart rsyslog
systemctl restart rsyslog

# Copy configuration template to /etc/gotham
#mkdir /etc/gotham/
#cp $GOTHAM_HOME/Orchestrator/Config/config.ini

# Configure database
mysql -u root -e "CREATE DATABASE GOTHAM;"
mysql -u root GOTHAM < $GOTHAM_HOME/Orchestrator/Internal_Database/gotham.sql

source /etc/profile
