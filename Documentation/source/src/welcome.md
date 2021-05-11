# GOTHAM
Global Orchestrator for Threat-intel through Honeypot Army Management

# Presentation

The aim of this project is to respond to 3 challenges : 

* Honeypots generates heterogenous data
* the relevance of a honeypot's location varies over time
* a large number of honeypots are need to cover as many vulnerabilities as possible

The GOTHAM project presents itself as an orchestrator. At first, this orchestrator is able to collect and harmonize data from many honeypots. Then, it proposes to ease the administration of honeypots by adding an abstraction layer over technical things (honeypots, servers, etc...). Therefore the user no longer needs to know where and how a honeypot is hosted.

Honeypots are made accessible through reverse-proxies which are scattered across different networks and geographic areas. This specificity allows users to modify the perceptible location of a honeypot.

Overall, the orchestrator follows a simple logic : it deals with 3 objects only.

* Honeypots :containers hosting vulnerable services
* Severs : servers hosting reverse-proxy service
* Network links : redirection of flows from reverse-proxies to honeypots

# This documentation

Firstly, this documentation cover installation subjects :

* Preparation & installation of the orchestrator
* Preparation of datacenter
* Preparation of servers

Secondly, the documentation presents some usecase :
* How to manage honeypots
* How to manage servers
* How to manage links
