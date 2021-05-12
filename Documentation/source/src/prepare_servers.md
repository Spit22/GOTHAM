# Servers preparation

First, you can run the server's preparation script :

```
$ curl https://raw.githubusercontent.com/Spit22/GOTHAM/master/Install/install_server.sh | sudo bash
```

The script will perform some tasks to prepare your server to become a datacenter :
  - add a gotham user
  - install dependancies
  - install nginx reverse-proxy from sources
  - create directories
  - etc.

Please note that this script is under development, so we don't provide any warranty on its behavior.

Once the script finished, it returns the base64 encoded ssh key of gotham user. Just copy it into the ssh_key POST param when adding the server with the API.

/!\ Note that in a production environment, we recommand you to manually install and configure your datacenter.
