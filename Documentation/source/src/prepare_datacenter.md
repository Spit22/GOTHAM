# Datacenter preparation

First, you can run the datacenter's preparation script :

```
$ curl -s https://github.com/Spit22/GOTHAM/blob/dev_V1_1/Install/install_dc.sh | sudo bash
```

The script will perform some tasks to prepare your server to become a datacenter :
  - add a gotham user
  - install dependancies
  - install docker
  - create directories
  - etc.

Please note that this script is under development, so we don't provide any warranty on its behavior.

Once the script finished, it returns the base64 encoded ssh key of gotham user. Just copy it to the orchestrator's configuration, on the datacenter section.

/!\ Note that in a production environment, we recommand you to manually install and configure your datacenter.
