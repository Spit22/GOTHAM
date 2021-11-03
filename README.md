<p align="center">
  <img src="https://user-images.githubusercontent.com/60015417/119951443-40ecdb80-bf9c-11eb-8e77-8bdb42243580.png"/>
</p>

# GOTHAM

Global Orchestrator for Threat-intel through Honeypot Army Management


[![Documentation Status](https://readthedocs.org/projects/gotham/badge/?version=latest)](https://gotham.readthedocs.io/en/latest/?badge=latest) ![GitHub](https://img.shields.io/github/license/spit22/GOTHAM) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/spit22/GOTHAM) [![GOTHAM application](https://github.com/Spit22/GOTHAM/actions/workflows/gotham_pipeline.yml/badge.svg)](https://github.com/Spit22/GOTHAM/actions/workflows/gotham_pipeline.yml)

# The project

Welcome to the GOTHAM Project !

GOTHAM is an orchestrator of honeypots. His reason of being is to respond to these 3 challenges : 

* Honeypots generates heterogenous data
* the relevance of the location of a honeypot varies over time
* a large number of honeypots are needed to cover as many vulnerabilities as possible

At first, this orchestrator is able to collect and harmonize data from many honeypots. Then, it proposes to ease the administration of honeypots by adding an abstraction layer over technical things (honeypots, servers, etc...). Therefore the user no longer needs to know where and how a honeypot is hosted.

Honeypots are made accessible through reverse-proxies which are scattered across different networks and geographic areas. This specificity allows users to modify the perceptible location of a honeypot.

To implement these features, the orchestrator follows a simple logic : it deals with 3 objects only.

* Honeypots : docker containers hosting vulnerable services
* Severs : servers hosting reverse-proxy services
* Network links : redirection of flows from one or more reverse-proxies to one or more honeypots

# Get started

## Install orchestrator

Installation script for orchestrator is available :

```
curl -s https://raw.githubusercontent.com/Spit22/GOTHAM/master/Install/install_orchestrator.sh | sudo bash
```

Apply GOTHAM's environment variables :

```
source /etc/profile
```

Lauch orchestrator's API :

```
python3 /opt/GOTHAM/Orchestrator/Sources/api.py3
```

## Install datacenter

Installation script for datacenter is available :

```
curl -s https://raw.githubusercontent.com/Spit22/GOTHAM/master/Install/install_dc.sh | sudo bash
```

## Install a server

Installation script for server is available :

```
curl -s https://raw.githubusercontent.com/Spit22/GOTHAM/master/Install/install_server.sh | sudo bash
```

To get an overview of GOTHAM capabilities, consult the documentation.

## Install gothamctl

```
git clone https://github.com/Spit22/GOTHAM.git
cd $GOTHAM_HOME/Gothamctl/
ln -s $GOTHAM_HOME/Gothamctl/gothamctl.py /usr/sbin/gothamctl
```


# Documentation

All technical and functional documentation is available at https://gotham.readthedocs.io/en/latest/index.html


