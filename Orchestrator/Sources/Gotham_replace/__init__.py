from . import replace_functions
import Gotham_normalize
import Gotham_SSH_SCP

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def replace_hp_for_rm(DB_settings, datacenter_settings, hp_infos):
    '''
    Try to replace the honeypot for each of its links, or take care of its
    removal in the affected links

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        hp_infos (dict) : honeypot information subject to deletion

    Raise error if something failed
    '''

    # Formatting in display format of honeypot information if this is not
    # already the case
    if not("links" in hp_infos.keys()):
        hp_infos = Gotham_normalize.normalize_display_object_infos(
            hp_infos,
            "hp"
        )

    all_ok = True

    # Try to replace with one hp for all link
    result = False
    try:
        result = replace_functions.replace_honeypot_all_link(
            DB_settings,
            datacenter_settings,
            hp_infos
        )
    except Exception as e:
        raise ValueError(
            "Error while replacing one hp for all links : " + str(e))

    # if we can't, just find a honeypot per link
    if not(result):
        # Save duplicate hps in this change so as not to reduplicate them
        duplicate_hp_list = []
        # Initialization of the variable storing the result
        res = {}
        # Loop through all links using honeypot subject to deletion
        for link in hp_infos["links"]:
            try:
                # Try to replace the honeypot in each link
                res = replace_functions.replace_honeypot_in_link(
                    DB_settings,
                    datacenter_settings,
                    hp_infos,
                    link,
                    duplicate_hp_list=duplicate_hp_list
                )
                result = res["replaced"]
                duplicate_hp_list = res["duplicate_hp_list"]
            except Exception as e:
                raise ValueError(
                    "Error while changing hp for a link : " + str(e))

            # If we can't replace, just edit link to decrease nb hp
            if not(result):
                try:
                    result = replace_functions.decrease_link(
                        DB_settings,
                        datacenter_settings,
                        hp_infos,
                        link,
                        "hp"
                    )
                except Exception as e:
                    raise ValueError(
                        "Error decreasing the hp number of link : " + str(e))
                if not(result):
                    all_ok = False

    return all_ok


def replace_hp_for_deleted_tags(DB_settings, datacenter_settings,
                                hp_infos, deleted_tags):
    '''
    Try to replace the honeypot for each of its links with concerned tags,
    or take care of its removal in the affected links

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        hp_infos (dict) : honeypot information subject to deletion
        deleted_tags (string) : list of tags which are subject to deletaion

    Raise error if something failed
    '''

    # Formatting in display format of honeypot information if this is not
    # already the case
    if not("links" in hp_infos.keys()):
        hp_infos = Gotham_normalize.normalize_display_object_infos(
            hp_infos,
            "hp"
        )

    # Save duplicate hps in this change so as not to reduplicate them
    duplicate_hp_list = []
    # Initialization of the variable storing the result
    res = {}

    all_ok = True
    # Loop through all links using honeypot subject to deletion
    for link in hp_infos["links"]:
        # Check if the link uses the tags which are subject to deletaion
        present_in_link = list(set(deleted_tags) & set(
            link["link_tags_hp"].split("||")))

        # If some tags are used
        if present_in_link != []:
            result = False
            # Try to replace
            try:
                # Try to replace the honeypot in each link
                res = replace_functions.replace_honeypot_in_link(
                    DB_settings,
                    datacenter_settings,
                    hp_infos,
                    link,
                    duplicate_hp_list
                )
                result = res["replaced"]
                duplicate_hp_list = res["duplicate_hp_list"]
            except Exception as e:
                raise ValueError(e)

            # If we can't replace, just edit link to decrease nb hp
            if not(result):
                try:
                    result = replace_functions.decrease_link(
                        DB_settings,
                        datacenter_settings,
                        hp_infos,
                        link,
                        "hp"
                    )
                except Exception as e:
                    raise ValueError(e)
                if not(result):
                    all_ok = False
    return all_ok


def replace_hp_for_added_tags_in_link(DB_settings, datacenter_settings,
                                      link_infos, hp_infos, new_tags):
    '''
    Try to replace the honeypot for its links with additional tags,
    or take care of its removal in the affected links

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        link_infos (dict) : link information subject to edition
        hp_infos (dict) : honeypot information subject to replacement
        new_tags (string) : list of new tags add in the link

    Raise error if something failed
    '''

    all_ok = True

    # Try to replace the honeypot in the link
    try:
        res = replace_functions.replace_honeypot_in_link(
            DB_settings,
            datacenter_settings,
            hp_infos,
            link_infos,
            duplicate_hp_list=[],
            new_tags=new_tags
        )
        result = res["replaced"]
    except Exception as e:
        raise ValueError(e)

    # If we can't replace, just edit link to decrease nb hp
    if not(result):
        try:
            result = replace_functions.decrease_link(
                DB_settings,
                datacenter_settings,
                hp_infos,
                link_infos,
                "hp"
            )
        except Exception as e:
            raise ValueError(e)
        if not(result):
            all_ok = False

    return all_ok


def replace_serv_for_rm(DB_settings, datacenter_settings, serv_infos):
    '''
    Try to replace the server for each of its links, or take care of
    its removal in the affected links

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        serv_infos (dict) : server information subject to deletion

    Raise error if something failed
    '''

    all_ok = True

    # Formatting in display format of server information if this is not
    # already the case
    if not("links" in serv_infos.keys()):
        serv_infos = Gotham_normalize.normalize_display_object_infos(
            serv_infos,
            "serv"
        )

    # Try to replace link by link
    for link in serv_infos["links"]:
        result = False
        # Try to replace
        try:
            result = replace_functions.replace_server_in_link(
                DB_settings,
                serv_infos,
                link
            )
        except Exception as e:
            raise ValueError(e)

        # If we can't replace, just edit link to decrease nb serv
        if not(result):
            try:
                result = replace_functions.decrease_link(
                    DB_settings,
                    datacenter_settings,
                    serv_infos,
                    link,
                    "serv"
                )
            except Exception as e:
                raise ValueError(e)
            if not(result):
                all_ok = False

    return all_ok


def replace_serv_for_deleted_tags(DB_settings, datacenter_settings,
                                  serv_infos, deleted_tags):
    '''
    Try to replace the server for each of its links with concerned tags,
    or take care of its removal in the affected links

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        serv_infos (dict) : server information subject to deletion
        deleted_tags (string) : list of tags which are subject to deletion

    Raise error if something failed
    '''

    all_ok = True

    # Formatting in display format of server information if this is not
    # already the case
    if not("links" in serv_infos.keys()):
        serv_infos = Gotham_normalize.normalize_display_object_infos(
            serv_infos,
            "serv"
        )

    # Loop through all links using honeypot subject to deletion
    for link in serv_infos["links"]:
        # Check if the link uses the tags which are subject to deletaion
        present_in_link = list(set(deleted_tags) & set(
            link["link_tags_serv"].split("||")))

        # If some tags are used
        if present_in_link != []:
            result = False
            # Try to replace
            try:
                result = replace_functions.replace_server_in_link(
                    DB_settings,
                    serv_infos,
                    link
                )
            except Exception as e:
                raise ValueError(e)

            # If we can't replace, just edit link to decrease nb serv
            if not(result):
                try:
                    result = replace_functions.decrease_link(
                        DB_settings,
                        datacenter_settings,
                        serv_infos,
                        link,
                        "serv"
                    )
                except Exception as e:
                    raise ValueError(e)
                if not(result):
                    all_ok = False

            # If we have succeeded in replacing or deleting the server in the
            # link, we delete the nginx conf of the concerned link
            if result:
                try:
                    commands = ["rm /etc/nginx/conf.d/links/" +
                                link["link_id"] + "-*.conf"]
                    Gotham_SSH_SCP.execute_commands(
                        serv_infos["serv_ip"],
                        serv_infos["serv_ssh_port"],
                        serv_infos["serv_ssh_key"],
                        commands
                    )
                    return True
                except Exception as e:
                    logging.error(
                        f"{link['link_id']} removal on servers failed : {e}")
                    raise ValueError(e)
    return all_ok


def replace_serv_for_added_tags_in_link(DB_settings, datacenter_settings,
                                        link_infos, serv_infos, new_tags,
                                        already_used):
    '''
    Try to replace the server for its links with additional tags,
    or take care of its removal in the affected links

    ARGUMENTS:
    DB_settings (json) : auth information
    datacenter_settings (json) : datacenter auth information
    link_infos (dict) : link information subject to edition
    serv_infos (dict) : server information subject to replacement
    new_tags (string) : list of new tags add in the link

    Raise error if something failed
    '''

    result = False
    # Try to replace the server in the link
    try:
        result = replace_functions.replace_server_in_link(
            DB_settings,
            serv_infos,
            link_infos,
            new_tags=new_tags,
            already_used=already_used
        )
    except Exception as e:
        raise ValueError(e)

    # If we can't replace, just edit link to decrease nb serv
    if not(result):
        try:
            result = replace_functions.decrease_link(
                DB_settings,
                datacenter_settings,
                serv_infos,
                link_infos,
                "serv"
            )
        except Exception as e:
            raise ValueError(e)

    else:
        return result

    # If we have succeeded in replacing or deleting the server in the link, we
    # delete the nginx conf of the concerned link
    if result:
        try:
            commands = ["rm /etc/nginx/conf.d/links/" +
                        link_infos["link_id"] + "-*.conf"]
            Gotham_SSH_SCP.execute_commands(
                serv_infos["serv_ip"],
                serv_infos["serv_ssh_port"],
                serv_infos["serv_ssh_key"],
                commands
            )
            return already_used
        except Exception as e:
            logging.error(
                f"{link_infos['link_id']} removal on servers failed : {e}")
            raise ValueError(e)
    else:
        already_used[0] = "KO"
        return already_used


def distrib_servers_on_link_ports(DB_settings, link):
    '''
    Try to distribute the exposure ports on the servers according to
    the specifications of the link

    ARGUMENTS:
        DB_settings (json) : auth information
        link (dict) : link information subject to redistribution

    Raise error if something failed
    '''
    try:
        replace_functions.distribute_servers_on_link_ports(DB_settings, link)
    except Exception as e:
        raise ValueError(e)


def config_honeypot_replacement(DB_settings, datacenter_settings,
                                old_hp_infos, new_hp_infos={}, link=None):
    '''
    Configure all the objects for the replacement of a honeypot

    ARGUMENTS:
        DB_settings (json) : auth information
        datacenter_settings (json) : datacenter auth information
        old_hp_infos (dict) : old honeypot information subject to replacement
        new_hp_infos (dict) - optional : new honeypot information for
            remplacement
        link (dict) - optional : link information subject to redistribution

    Raise error if something failed
    '''
    try:
        replace_functions.configure_honeypot_replacement(
            DB_settings,
            datacenter_settings,
            old_hp_infos,
            new_hp_infos=new_hp_infos,
            link=link
        )
    except ValueError as e:
        raise ValueError(e)
