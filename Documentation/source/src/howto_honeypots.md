# Honeypots Management

### Quésaco ?

In GOTHAM projet, a honeypot is a docker container that expose a vulnerable service to hackers on the internet, throught servers objects.

### How to add a honeypot to GOTHAM ?

#### Using direct API requests

First, you have to create the honeypot-definition file :

```
    {
        "name": "My first Honeypot",
        "descr": "A documentation POC",
        "tags": "France,AS_4242,CVE-2020-1456,Apache",
        "parser": "%host %timestamp %message",
        "logs": "/var/log/lastlog",
        "dockerfile": "RlJPTSBodHRwZDpsYXRlc3QK",
        "port": "80",
        "autotags": 1
    }

```

Here some explanations :
* 'name' field permits to define the honeypot's name
* 'descr' field permits to add some text useful to identify the honeypot
* 'tags' field permits to add some tags (coma separated) that desscribes the honeypot (Geolocation, logical-location, CVEs, network, OS, etc.)
* 'parser' field permits to define how the orchestrator has to parse honeypot's logs
* 'logs' field define the path to log the orchestrator has to monitor on the honeypot
* 'dockerfile' field contains base64 encoded dockerfile (here, it is the base64 of "FROM httpd:latest")
* 'port' field define which port has to be exposed on the honeypot
* 'autotags' field contains a boolean (1 or 0) to decide if you want orchestrator to automatically add tags to honeypot (using a Trivy scan)

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/add/honeypot --data-binary @new_hp.json -H "Content-Type: application/json"
```

If GOTHAM returns an id, the honeypot was successfully generated on the datacenter.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py add hp -name NAME -descr DESCR -tag TAGS -parser PARSER -logs LOGS -src DOCKERFILE_PATH -port PORT [-autotags]
```

### How to remove a honeypot on GOTHAM ?
Note : if you try to remove a honeypot that is used by a link, GOTHAM will automatically duplicate the removed honeypot on another container, to maintain the link definition terms. If you want to totally remove a honeypot, you have to check that it is not used on some links.
#### Using direct API requests
Following command permits to remove a honeypot from its id :
```
curl -X POST http://[gotham's api]:[port]/rm/honeypot -d {"id": "[hp_id]"} -H "Content-Type: application/json"
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py rm hp -id [hp_id]
```

### How to edit a honeypot on GOTHAM ?

#### Using direct API requests

First, you have to create the honeypot-definition file (which only contains information you want to change) :

```
    {
        "id": "[hp_id]",
        "logs": "/opt/honeypot/nginx.log"
    }

```
With this file, the honeypot's monitored logs will be changed. You can change whatever you want, as fields are same as the add section.

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/edit/honeypot --data-binary @edit_hp.json -H "Content-Type: application/json"
```

If GOTHAM returns new honeypot information, the honeypot was successfully edited on the datacenter.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
gothamctl.py edit hp -id ID [-name NAME] [-descr DESCR] [-tag TAG] [-parser PARSER] [-logs LOGS] [-src SRC] [-port PORT]
```

### How to list all honeypots on GOTHAM ?

#### Using direct API requests

Following command return a json formatted list of all honeypots managed by GOTHAM :
```
curl -X GET http://[gotham's api]:[port]/list/honeypot
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls hp
```

### How to show information of a specific honeypot on GOTHAM ?

#### Using direct API requests

Following command return a json formatted information list of provided honeypot :
```
curl -X GET http://[gotham's api]:[port]/list/honeypot?id=[hp_id]
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls hp -id HP_ID
```
