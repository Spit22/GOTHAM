# Link Management

### Quésaco ?

In GOTHAM projet, a link is an abstract object that permit a honeypot to be exposed on a server. In other terms, it correspond to the redirection FROM a server TO a honeypot.

### How to add a link to GOTHAM ?

#### Using direct API requests

First, you have to create the link-definition file :

```
  {
        "tags_serv": "France",
        "tags_hp": "Apache",
        "nb_hp": "4",
        "nb_serv": "2",
        "exposed_ports": "80,8080,443",
    }

```

Here some explanations :
* 'tags_hp' field permits to define which type of honeypot we want to expose
* 'tags_serv' field permits to define on which type of server we want to expose honeypots
* 'nb_hp' field corresponds to the amount of honeypot that we want to integrate to the link. There is two cases :
  * provided nb_hp > actual nb_hp : in this case, GOTHAM will choose the most relevant honeypots, and duplicate them.
  * provided nb_hp < actual nb_hp : in this case, GOTHAM will choose the most relevant honeypots, and use them.
* 'nb_serv' field corresponds to the amount of server used to expose honeypots. Provided nb_serv has to be inferior or equal to the actual number of servers managed by GOTHAM.
* 'exposed_ports' field contains coma-separated list of port on which honeypots are exposed to the internet

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/add/link --data-binary @new_link.json -H "Content-Type: application/json"
```

If GOTHAM returns an id, the link is now completely configured.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
gothamctl.py add link [-h] -tags_hp TAGS_HP -tags_serv TAGS_SERV -ports PORTS -nb_hp NB_HP -nb_serv NB_SERV
```

### How to remove a link on GOTHAM ?

#### Using direct API requests
Following command permits to remove a link from its id :
```
curl -X POST http://[gotham's api]:[port]/rm/link -d {"id": "[link_id]"} -H "Content-Type: application/json"
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py rm link -id [link_id]
```

### How to edit a link on GOTHAM ?

#### Using direct API requests

First, you have to create the link-definition file (which only contains information you want to change) :

```
    {
        "id": "[link_id]",
        "nb_hp": "5"
    }

```
With this file, GOTHAM will duplicate or add some honeypots to include them to the link. You can change whatever you want, as fields are same as the add section.

Once you have created you own definition file, you can send it to the orchestrator's api :

```
curl -X POST http://[gotham's api]:[port]/edit/link --data-binary @edit_link.json -H "Content-Type: application/json"
```

If GOTHAM returns new link information, the link was successfully edited.

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
gothamctl.py edit link -id ID [-tags_hp TAGS_HP] [-tags_serv TAGS_SERV] [-nb_hp NB_HP] [-nb_serv NB_SERV] [-ports PORTS]
```

### How to list all links on GOTHAM ?

#### Using direct API requests

Following command return a json formatted list of all links configured by GOTHAM :
```
curl -X GET http://[gotham's api]:[port]/list/links
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls link
```

### How to show information of a specific link on GOTHAM ?

#### Using direct API requests

Following command return a json formatted description of provided link :
```
curl -X GET http://[gotham's api]:[port]/list/link?id=[link_id]
```

#### Using gothamctl

The gothamctl command is easier than the previous method :
```
 gothamctl.py ls lin -id LINK_ID
```
