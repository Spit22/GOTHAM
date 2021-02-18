# -*- coding: utf-8 -*-
# Import external libs
from io import StringIO
import base64
import sys
import configparser

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import rm_hp

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands

def edit_tags(DB_settings, honeypot, tags):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    
    #port_separator = config['port']['separator']
    #mod_honeypot=honeypot
    
    old_tags=honeypot["hp_tags"].split("||")
    new_tags=tags.split(tags_separator)

    deleted_tags=list(set(old_tags)-set(new_tags))

    dsp_honeypot=Gotham_normalize.normalize_display_object_infos(honeypot,"hp")

    for deleted_tag in deleted_tags:
        duplicate_hp_list=[]
        i = 0
        for link in dsp_honeypot["links"]:
            if deleted_tag in link["link_tags_hp"].split("||"):
                
                
                    replaced=False
                    link_tags_hp=tags_separator.join(link["link_tags_hp"].split("||"))

                    # Get all honeypots corresponding to tags
                    honeypots = Gotham_check.check_tags("hp",Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=link_tags_hp), tags_hp=link_tags_hp)

                    # Filter honeypots in error, and original hp by id
                    honeypots = [hp for hp in honeypots if not(hp["hp_state"]=='ERROR' or hp["hp_id"]==dsp_honeypot["hp_id"])]

                    if honeypots!=[]:
                        already_duplicate_weight=int(config['hp_weight']["already_duplicate"])
                        honeypots=[dict(hp, **{'weight':already_duplicate_weight}) if hp["hp_id"] in duplicate_hp_list else hp for hp in honeypots]
                        # Choose best honeypots (the lower scored)
                        honeypots = Gotham_choose.choose_honeypots(honeypots, 1, link_tags_hp)

                        if honeypots[0]["hp_id"] in duplicate_hp_list:
                            # Don't duplicate, just configure
                            honeypot=honeypots[0]
                        else:
                            # Duplicate, and configure
                            honeypot=rm_hp.duplicate_hp(DB_settings,honeypots)
                            duplicate_hp_list.append(honeypot["hp_id"])
                        try:
                            rm_hp.configure_honeypot_replacement(DB_settings,dsp_honeypot, new_hp_infos=honeypot, num_link=i)
                        except:
                            sys.exit(1)
                            
                        modifs={"id_hp":honeypot["hp_id"]}
                        conditions={"id_link":link["link_id"],"id_hp":honeypot["hp_id"]}
                        try:
                            Gotham_link_BDD.edit_lhs_DB(DB_settings,modifs,conditions)
                        except:
                            sys.exit(1)
                        replaced=True

                    # If we can't replace, just edit link to decrease nb hp
                    if replaced==False:
                        if int(link["link_nb_hp"]) > 1:
                            # Configure all server to not redirect on hp
                            try:
                                rm_hp.configure_honeypot_replacement(DB_settings,dsp_honeypot,num_link=i)
                            except:
                                sys.exit(1)

                            try:
                                Gotham_link_BDD.remove_lhs(DB_settings,id_link=link["link_id"], id_hp=dsp_honeypot["hp_id"])
                            except:
                                sys.exit(1)
                            try:
                                modifs={"nb_hp":int(link["link_nb_hp"])-1}
                                conditions={"id":link["link_id"]}
                                Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
                            except:
                                sys.exit(1)
                        else:        
                            # If nb hp=1, error, we can't do nothing
                            logging.error(f"You tried to remove a running honeypot with the id = {id}, and it can't be replaced or deleted")
                            sys.exit(1)
            i = i + 1