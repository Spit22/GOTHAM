# Append Sources folder path to be able to import the libraries inside
import sys
sys.path.append('/home/spitfire/GOTHAM/Orchestrator/Sources')

# Import libraries
from Gotham_link_BDD import get_server_infos, get_tag_infos

def server(DB_settings, ip):
    # Check if a server is already present in database
    #
    # DB_settings (json) : auth information
    # ip (string) : ip of the server we want to check
    #
    # Return True if already exists, False in the other case

    response = get_server_infos(DB_settings, ip=ip)
    return not(response == [])

def tag(DB_settings, tag):
    # Check if a tag is already present in database
    #
    # DB_settings (json) : auth information
    # tag (string) : tag we want to check
    #
    # Return True if already exists, False in the other case

    response = get_tag_infos(DB_settings, tag=tag)
    return not(response == [])
