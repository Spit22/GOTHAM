#!/bin/bash

# Update repository
apt update

# Install needed packages
apt install -y python3 python3-pip git mariadb-server

# Install libs
apt install -y libmariadb-dev

# Configure $GOTHAM_HOME var
echo -e "\nexport GOTHAM_HOME=/opt/GOTHAM/" >> /etc/profile
GOTHAM_HOME=/opt/GOTHAM/

# Going to /opt to install GOTHAM
cd /opt

# Clone repository on this directory
git clone https://github.com/Spit22/GOTHAM
chown -R gotham-admin:root $GOTHAM_HOME


# Going on the repository folder
cd $GOTHAM_HOME/Orchestrator/Sources

# Choose the git branch
git checkout dev_V0_1


# Install all python libs
pip3 install -r requirements.txt

# Create /data to store GTOAHM's data
mkdir -p /data/template
mkdir -p 

# Copy configuration template to /etc/gotham
#mkdir /etc/gotham/
#cp $GOTHAM_HOME/Orchestrator/Config/config.ini

# Configure database
mysql -u root -e "CREATE DATABASE GOTHAM;"
mysql -u root GOTHAM < $GOTHAM_HOME/Orchestrator/Internal_Database/gotham.sql
