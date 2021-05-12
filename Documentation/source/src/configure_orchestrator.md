# GOTHAM configuration

You can configure your orchestrator under $INSTALL_PATH/Orchestrator/Config/config.ini.

The following list cover all sections supported in the configuration file :
  - [tag] section permits to define how GOTHAM will deal with object's tags
  - [trivy] section defines options passed to trivy for the honeypot autotag feature
  - [ipstack] section defines access and options passed to the ipstack api for the server autotag feature
  - [port] sections permits to define how GOTHAM will deal with object's ports
  - [server_infos_default] sections defines which are the default values when they are not provided on server creation
  - [honeypot_infos_default] sections defines which are the default values when they are not provided on honeypot creation
  - [link_infos_default] sections defines which are the default values when they are not provided on honeypot creation
  - [state] defines which state can be used for both honeypots and servers
  - [weight_base] defines default weight for both honeypots and servers
  - [hp_weight] section permits to define how GOTHAM will process honeypot weigth calculation
  - [serv_weight] section permits to define how GOTHAM will process server weigth calculation
  - [datacenter] sections defines how the orchestrator has to connect to datacenter
  - [internaldb] sections defines hwo GOTHAM has to connect to internal database
  - [orchestrator] sections defines some useful information for GOTHAM (like the ip address to use, the port on which syslog listen)

We will detail each sections by showing a configuration template.

### Tag
```
[tag]
separator = "separator to distinguish tags, may be a coma ','"
default_value = "value of the default tag, may be 'DEFAULT'"
```

### Trivy
```
[trivy]
version = "trivy version"
template = "trivy template to use"
options = "trivy options, can be empty"
separator = "may be a coma ','"
```

### Ipstack
```
[ipstack]
access_key = "ipstack api key"
parser = "parser to use"
```

### Port
```
[port]
separator = "separator to distinguish ports, may be a coma ','"
```

### Server_infos_default
```
[server_infos_default]
id = "default id"
name = "default name"
descr = "default description"
ip = "default ip"
ssh_key = "default base64 encodedssh_key"
ssh_port = "default ssh port"
state = "default state"
tags = "default tags"
```

### Honeypot_infos_default
```
[honeypot_infos_default]
id = "default id"
name = "default name"
descr = "default description"
parser = "default parser"
logs = "default logs path"
source = "default base64 encoded dockerfile"
port_container = "default port_container"
state = "default state"
tags = "default tags"
```

### Link_infos_default
```
[link_infos_default]
id = "default id"
nb_hp = "default nb_hp"
nb_serv = "default nb_serv"
tags_hp = "default tags_hp"
tags_serv = "default tags_serv"
```

### State
```
[state]
hp_state = "coma-separated possible states"
serv_state = "coma-separated possible states"
```

### Weight_base
```
[weight_base]
hp = "default honeypot weight"
serv = "default server weight"
```

### Hp_weight
```
[hp_weight]
UNUSED = "Weight to apply when the honeypot has this state"
HEALTHY = "Weight to apply when the honeypot has this state"
ERROR = "Weight to apply when the honeypot has this state"
DOWN = "Weight to apply when the honeypot has this state"
duplicat = "Weight to apply when the honeypot is a duplicate"
nb_link = "Weight to apply when the honeypot has nb_link links"
nb_useless_tag = "Weight to apply when the honeypot has nb_useless_tags useless tags"
created_at = "Weight to apply to the caracteristic created_at"
updated_at = -50
already_duplicate = "Weight to apply to the caracteristic updated_at"
```

### Serv_weight
```
[serv_weight]
UNUSED = "Weight to apply when the server has this state"
HEALTHY = "Weight to apply when the server has this state"
ERROR = "Weight to apply when the server has this state"
DOWN = "Weight to apply when the server has this state"
nb_link = "Weight to apply when the server has nb_link links"
nb_port_used =  "Weight to apply when the server has nb_ports_used used ports"
nb_useless_tag =  "Weight to apply when the server has nb_useless_tags useless tags"
nb_free_port =  "Weight to apply when the server has nb_free_ports free ports"
created_at = "Weight to apply to the caracteristic created_at"
updated_at = "Weight to apply to the caracteristic updated_at"
```

### Datacenter
```
[datacenter]
ip = "datacenter ip"
ssh_port = "datacenter ssh port"
ssh_key = "datacenter ssh key for gotham user"
min_port = "minimum port to be used for honeypots exposition"
max_port = "maximum port to be used for honeypots exposition"
```

### Internaldb
```
[internaldb]
username = "mysql user"
password = "mysql password"
hostname = "mysql ip"
port = "mysql port"
database = "mysql database"
```

### Orchestrator
```
[orchestrator]
ip = "orchestrator's ip to use"
syslog_port = "syslog port, may be 1514"
```
