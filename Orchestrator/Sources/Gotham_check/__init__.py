from . import check_SSH
from . import check_PING
from . import check_DOUBLON

def check_ssh(ip, ssh_port, used_ssh_key):
    return check_SSH.main(ip, ssh_port, used_ssh_key)

def check_ping(hostname):
    return check_PING.main(hostname)

def check_doublon_server(DB_settings, ip):
    return check_DOUBLON.server(DB_settings, ip)

def check_doublon_tag(DB_settings, tag):
    return check_DOUBLON.tag(DB_settings, tag)
    