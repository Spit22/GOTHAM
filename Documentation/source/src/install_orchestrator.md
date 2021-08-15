# Orchestrator installation

First, you can run the orchestrator's installation script :

```
$ curl -s https://raw.githubusercontent.com/Spit22/GOTHAM/dev_V1/Install/install_orchestrator.sh | sudo bash
```

The script will perform some tasks to prepare your server to become an orchestrator :
  - add a gotham user
  - install dependancies
  - install GOTHAM from sources
  - create directories
  - etc.

.. warning::

  Please note that this script is under development, so we don't provide any warranty on its behavior.


Once the script finished, you can retrieve GOTHAM on ``/opt/GOTHAM``.

Then you have to define GOTHAM_HOME by :

```
$ source /etc/profile
```

And it's all. You can now configure your orchestrator under ``/opt/GOTHAM/Orchestrator/Config/config.ini``. Please refer to the configuration documentation for that part.

To run the orchestrator's api, you have to execute the following command :

```
# Run API
$ python3 /opt/GOTHAM/Orchestrator/Sources/api.py3
# Run the watchconfig daemon
$ python3 /opt/GOTHAM/Orchestrator/Sources/watchconfig.py
```


The api will listen on port 5000 on localhost by default. Please use Apache or Nginx for reverse proxying and expose api to another network. 

/!\ Note that in a production environment, we recommand you to create an init script, to run GOTHAM as a service and not as a simple python command.
