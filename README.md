# GOTHAM
Global Orchestrator for Threat-intel through Honeypot Army Management

[![Documentation Status](https://readthedocs.org/projects/gotham/badge/?version=latest)](https://gotham.readthedocs.io/en/latest/?badge=latest)

![Language used](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![GitHub](https://img.shields.io/github/license/spit22/GOTHAM)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/spit22/GOTHAM)

# The project

The aim of this project is to respond to 3 challenges : 

* Honeypots generates heterogenous data
* the relevance of the location of a honeypot varies over time
* a large number of honeypots are needed to cover as many vulnerabilities as possible

The GOTHAM project presents itself as an orchestrator. At first, this orchestrator is able to collect and harmonize data from many honeypots. Then, it proposes to ease the administration of honeypots by adding an abstraction layer over technical things (honeypots, servers, etc...). Therefore the user no longer needs to know where and how a honeypot is hosted.

Honeypots are made accessible through reverse-proxies which are scattered across different networks and geographic areas. This specificity allows users to modify the perceptible location of a honeypot.

To implement these features, the orchestrator follows a simple logic : it deals with 3 objects only.

* Honeypots :containers hosting vulnerable services
* Severs : servers hosting reverse-proxy service
* Network links : redirection of flows from reverse-proxies to honeypots

# The sources

Here are the details of the sources of the project :

* Orchestrator/Config : configuration files used by the orchestrator
* Orchestrator/Internal_Database : required files to set up the internal database
* Orchestrator/Logs : log files of the orchestrator
* Orchestrator/NGINX_scripts : required scripts to install NGINX on remote servers
* Orchestrator/Sources : source files of the project
* Orchestrator/Sources/Gotham_* : libraries used by the orchestrator