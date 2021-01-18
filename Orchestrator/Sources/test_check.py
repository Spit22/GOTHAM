##########-IMPORT SECTION-##########
from Gotham_check import check_ping, check_ssh, check_doublon_server, check_doublon_tag
import os
##########-IMPORT SECTION-##########

##########-SETTINGS-##########
# Environment variable
#Gotham_home = os.environ.get("GOTHAM_HOME")
Gotham_home = "/home/spitfire/GOTHAM"
# Database settings
DB_settings = {"username":"gotham", "password":"password", "hostname":"192.168.1.172", "port":"3306", "database":"GOTHAM"}
# Test server settings
hostname = "172.0.0.1"
ssh_port = "22"
ssh_key_path = Gotham_home+"/Orchestrator/Safe/test_key"
##########-SETTINGS-##########

##########-TESTS-##########
print("####################")
#print(check_ping(hostname))
print("####################")
#print(check_ssh(hostname, ssh_port, ssh_key_path))
print("####################")
#print(check_doublon_server(DB_settings, hostname))
print("####################")
print(check_doublon_tag(DB_settings, "DNS"))
##########-TESTS-##########