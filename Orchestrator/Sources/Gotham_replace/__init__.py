import sys
import configparser
import os
from . import replace_functions

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_SSH_SCP
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def replace_hp_for_rm(DB_settings, datacenter_settings, hp_infos):

  if not("links" in hp_infos.keys()):
    hp_infos=Gotham_normalize.normalize_display_object_infos(hp_infos,"hp")

  # Try to replace with one hp for all link
  result=False
  try:
    result=replace_functions.replace_honeypot_all_link(DB_settings, datacenter_settings, hp_infos)
  except Exception as e:
      raise ValueError("Error while replacing one hp for all links : "+str(e))

  if result==False:
    # if not, just find a honeypot per link
    duplicate_hp_list = []
    res={}
    for link in hp_infos["links"]:
      try:
        res=replace_functions.replace_honeypot_in_link(DB_settings, datacenter_settings, hp_infos, link, duplicate_hp_list=duplicate_hp_list)
        result=res["replaced"]
        duplicate_hp_list=res["duplicate_hp_list"]
      except Exception as e:
          raise ValueError("Error while changing hp for a link : "+str(e))

      # If we can't replace, just edit link to decrease nb hp
      if result == False:
        try:
          replace_functions.decrease_link(DB_settings, datacenter_settings, hp_infos, link, "hp")
        except Exception as e:
            raise ValueError("Error decreasing the hp number of link : "+str(e))

def replace_hp_for_deleted_tags(DB_settings, datacenter_settings, hp_infos, deleted_tags):
  if not("links" in hp_infos.keys()):
    hp_infos=Gotham_normalize.normalize_display_object_infos(hp_infos,"hp")

  duplicate_hp_list = []
  res={}
  for link in hp_infos["links"]:
    present_in_link=list(set(deleted_tags) & set(link["link_tags_hp"].split("||")))
    
    if present_in_link != []:
      result=False
      # Try to replace
      try:
        res=replace_functions.replace_honeypot_in_link(DB_settings, datacenter_settings, hp_infos, link, duplicate_hp_list)
        result=res["replaced"]
        duplicate_hp_list=res["duplicate_hp_list"]
      except Exception as e:
        raise ValueError(e)

      # If we can't replace, just edit link to decrease nb hp
      if result == False:
        try:
          replace_functions.decrease_link(DB_settings, datacenter_settings, hp_infos, link, "hp")
        except Exception as e:
          raise ValueError("Olivier a fait de la merde n2")


def replace_serv_for_rm(DB_settings, datacenter_settings, serv_infos):

  if not("links" in serv_infos.keys()):
    serv_infos=Gotham_normalize.normalize_display_object_infos(serv_infos,"serv")

  
  # Try to replace link by link
  for link in serv_infos["links"]:
    result=False
    # Try to replace
    try:
      result = replace_functions.replace_server_in_link(DB_settings, serv_infos, link)
    except Exception as e:
        raise ValueError(e)

    # If we can't replace, just edit link to decrease nb serv
    if not(result):
      try:
        replace_functions.decrease_link(DB_settings, datacenter_settings, serv_infos, link, "serv")
      except Exception as e:
        raise ValueError(e)


def replace_serv_for_deleted_tags(DB_settings, datacenter_settings, serv_infos, deleted_tags):
  if not("links" in serv_infos.keys()):
    serv_infos=Gotham_normalize.normalize_display_object_infos(serv_infos,"serv")

  
  for link in serv_infos["links"]:
    present_in_link=list(set(deleted_tags) & set(link["link_tags_serv"].split("||")))
    
    if present_in_link != []:
      result=False
      # Try to replace
      try:
        result = replace_functions.replace_server_in_link(DB_settings, serv_infos, link)
      except Exception as e:
          raise ValueError(e)

      # If we can't replace, just edit link to decrease nb serv
      if not(result):
        try:
          replace_functions.decrease_link(DB_settings, datacenter_settings, serv_infos, link, "serv")
          result=True
        except Exception as e:
          raise ValueError(e)

      if result:
        try:
          commands = ["rm /etc/nginx/conf.d/links/" + link["link_id"] +"-*.conf"]
          Gotham_SSH_SCP.execute_commands(serv_infos["serv_ip"], serv_infos["serv_ssh_port"], serv_infos["serv_ssh_key"], commands)
          return True
        except Exception as e:
          logging.error(f"{link['link_id']} removal on servers failed : {e}")
          raise ValueError(e)


def replace_serv_for_added_tags_in_link(DB_settings, datacenter_settings, link_infos, serv_infos, new_tags, already_used):
  result=False
  # Try to replace
  try:
    result = replace_functions.replace_server_in_link(DB_settings, serv_infos, link_infos, new_tags=new_tags, already_used=already_used)
  except Exception as e:
      raise ValueError(e)

  # If we can't replace, just edit link to decrease nb serv
  if result == False:
    try:
      replace_functions.decrease_link(DB_settings, datacenter_settings, serv_infos, link_infos, "serv")
      result=True
    except Exception as e:
      raise ValueError(e)
  else:
    return result

  if result:
    try:
      commands = ["rm /etc/nginx/conf.d/links/" + link_infos["link_id"] +"-*.conf"]
      Gotham_SSH_SCP.execute_commands(serv_infos["serv_ip"], serv_infos["serv_ssh_port"], serv_infos["serv_ssh_key"], commands)
      return already_used
    except Exception as e:
      logging.error(f"{link_infos['link_id']} removal on servers failed : {e}")
      raise ValueError(e)


def replace_hp_for_added_tags_in_link(DB_settings, datacenter_settings, link_infos, hp_infos, new_tags):
  try:
    res=replace_functions.replace_honeypot_in_link(DB_settings, datacenter_settings, hp_infos, link_infos, duplicate_hp_list=[], new_tags=new_tags)
    result=res["replaced"]
  except Exception as e:
    raise ValueError(e)

  # If we can't replace, just edit link to decrease nb hp
  if result == False:
    try:
      replace_functions.decrease_link(DB_settings, datacenter_settings, hp_infos, link_infos, "hp")
    except Exception as e:
      raise ValueError(e)

def distrib_servers_on_link_ports(DB_settings, link):
  try:
    replace_functions.distribute_servers_on_link_ports(DB_settings, link)
  except Exception as e:
    raise ValueError(e)

def config_honeypot_replacement(DB_settings, datacenter_settings, old_hp_infos, new_hp_infos = {}, link = None):
  try:  
    replace_functions.configure_honeypot_replacement(DB_settings, datacenter_settings, old_hp_infos, new_hp_infos = new_hp_infos, link = link)
  except ValueError as e:
    raise ValueError(e)
