# -*- coding: utf-8 -*-
# Import Gotham's libs
# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_replace

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def edit_tags(DB_settings, link, tags, type_tag):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    port_separator = config['port']['separator']

    if type_tag!="hp" and type_tag!="serv":
        logging.error(f"type_tag is incorrect")
        sys.exit(1)

    new_tags=tags.split(tags_separator)
    
    dsp_link=Gotham_normalize.normalize_display_object_infos(link,"link",type_tag)

    already_used=[]
    for object_infos in dsp_link[type_tag+"s"]:
        not_present_in_obj=list(set(new_tags) - set(object_infos[type_tag+"_tags"].split("||")))
        if not_present_in_obj != []:
            links = Gotham_link_BDD.get_link_infos(DB_settings, id=dsp_link["link_id"])
            dsp_link=Gotham_normalize.normalize_display_object_infos(links[0],"link",type_tag)

            if type_tag=="serv":
                try:
                    already_used=Gotham_replace.replace_serv_for_added_tags_in_link(DB_settings, datacenter_settings, dsp_link, object_infos, tags, already_used)
                except:
                    sys.exit(1)
            
            elif type_tag=="hp":
                try:
                    Gotham_replace.replace_hp_for_added_tags_in_link(DB_settings, datacenter_settings, dsp_link, object_infos, tags)
                except:
                    sys.exit(1)