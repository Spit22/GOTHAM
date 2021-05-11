# Servers

### Quésaco ?

In GOTHAM projet, a server is a reverse-proxy exposing honeypots on the internet.

### How to add a server to GOTHAM ?

#### Using direct API requests

First, you have to create the server-definition file :

```
   {
        "ip": "1.2.3.4",
        "name": "Simple server",
        "descr": "Just a documentation POC",
        "tags": "Europe,France,Debian,Buster,AS_2021",
        "ssh_key": "[base64 encoded ssh_key returned by the installation script]",
        "ssh_port": "22",
        "autotags": 1
    }

```

Here some explanations :
* 'name' field permits to define the server's name
* 'descr' field permits to add some text useful to identify the server
* 'tags' field permits to add some tags (coma separated) that describes the server (Geolocation, logical-location, CVEs, network, OS, etc.)
* 'ssh_key' field define the ssh key that has to be used for ssh connection
* 'port' field define which port has to be used for ssh connection
* 'autotags' field contains a boolean (1 or 0) to decide if you want orchestrator to automatically add tags to server

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/add/server --data-binary @new_server.json -H "Content-Type: application/json"
```

If GOTHAM returns an id, the server is now completely managed.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
gothamctl.py add server -name NAME -descr DESCR -tag TAG -ip IP -key KEY -port PORT [-autotags]
```

### How to remove a server on GOTHAM ?
Note : if the server is actually used by a link, GOTHAM will automatically try to replace it with another server. If there is no other server available, GOTHAM will warn you with an error message and the server will not be removed.

#### Using direct API requests
Following command permits to remove a server from its id :
```
curl -X POST http://[gotham's api]:[port]/rm/server -d {"id": "[server_id]"} -H "Content-Type: application/json"
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py rm server -id [hp_id]
```

### How to edit a server on GOTHAM ?

#### Using direct API requests

First, you have to create the server-definition file (which only contains information you want to change) :

```
    {
        "id": "[server_id]",
        "ssh_key": "[new_sshkey]"
    }

```
With this file, the server's ssh key will be changed for next connections. You can change whatever you want, as fields are same as the add section.

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/edit/server --data-binary @edit_server.json -H "Content-Type: application/json"
```

If GOTHAM returns new server information, the server was successfully edited.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
gothamctl.py edit server -id SERVER_ID [-name NAME] [-descr DESCR] [-tag TAG] [-ip IP] [-key KEY] [-port PORT]
```

### How to list all servers on GOTHAM ?

#### Using direct API requests

Following command return a json formatted list of all servers managed by GOTHAM :
```
curl -X GET http://[gotham's api]:[port]/list/server
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls server
```

### How to show information of a specific server on GOTHAM ?

#### Using direct API requests

Following command return a json formatted description of provided server :
```
curl -X GET http://[gotham's api]:[port]/list/server?id=[server_id]
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls server -id SERVER_ID
```
