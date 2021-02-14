# Import external libs
import mariadb
import sys
import configparser

# Import Gotham's libs
from . import get_infos
from Gotham_normalize import normalize_honeypot_infos, normalize_server_infos, normalize_link_infos, normalize_lhs_infos, normalize_modif_to_str, normalize_conditions_to_str

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Retrieve settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
_separator = config['tag']['separator']


############################### TAG SECTION ###############################



############################### SERVER SECTION ###############################

def server(DB_connection, modifs, conditions):
    '''
    Edit Server table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    if [val for key, val in modifs.items() if 'tag' in key]!=[]:
        logging.error(f"Tags modification not implemented")
        sys.exit(1)

    if [val for key, val in conditions.items() if 'tag' in key]!=[]:
        logging.error(f"Modification by tag not implemented")
        sys.exit(1)


    # Normalize modifs
    try:
        modifs = normalize_server_infos(modifs)
    except:
        logging.error(f"Bad server modification")
        sys.exit(1)
    # Normalize conditions
    try:
        conditions = normalize_server_infos(conditions)
    except:
        logging.error(f"Bad server modif's conditions")
        sys.exit(1)

    # Prepare query
    ## Prepare modifs
    try:
        modifs = normalize_modif_to_str(modifs)
    except:
        logging.error(f"Can't prepare server modification")
        sys.exit(1)
    ## Prepare conditions
    try:
        conditions = normalize_conditions_to_str(conditions)
    except:
        logging.error(f"Can't prepare server modif's conditions")
        sys.exit(1)

    # Create the query
    query="UPDATE Server SET "+modifs+" WHERE "+conditions

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Edit values in Server table
        cur.execute(query)
        DB_connection.commit()
        logging.info(f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Server'")
    except mariadb.Error as e:
        logging.error(f"Modification failed -- SET {modifs}  WHERE {conditions} --  in the table 'Server' : {e}")
        sys.exit(1)
    



############################### HONEYPOT SECTION ###############################

def honeypot(DB_connection, modifs, conditions):
    '''
    Edit Honeypot table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    if [val for key, val in modifs.items() if 'tag' in key]!=[]:
        logging.error(f"Tags modification not implemented")
        sys.exit(1)

    if [val for key, val in conditions.items() if 'tag' in key]!=[]:
        logging.error(f"Modification by tag not implemented")
        sys.exit(1)


    # Normalize modifs
    try:
        modifs = normalize_honeypot_infos(modifs)
    except:
        logging.error(f"Bad honeypot modification")
        sys.exit(1)
    # Normalize conditions
    try:
        conditions = normalize_honeypot_infos(conditions)
    except:
        logging.error(f"Bad honeypot modif's conditions")
        sys.exit(1)

    # Prepare query
    ## Prepare modifs
    try:
        modifs = normalize_modif_to_str(modifs)
    except:
        logging.error(f"Can't prepare honeypot modification")
        sys.exit(1)
    ## Prepare conditions
    try:
        conditions = normalize_conditions_to_str(conditions)
    except:
        logging.error(f"Can't prepare honeypot modif's conditions")
        sys.exit(1)

    # Create the query
    query="UPDATE Honeypot SET "+modifs+" WHERE "+conditions

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Edit values in Honeypot table
        cur.execute(query)
        DB_connection.commit()
        logging.info(f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Honeypot'")
    except mariadb.Error as e:
        logging.error(f"Modification failed -- SET {modifs}  WHERE {conditions} --  in the table 'Honeypot' : {e}")
        sys.exit(1)
    

############################### LINK SECTION ###############################

def link(DB_connection, modifs, conditions):
    '''
    Edit Link table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    if [val for key, val in modifs.items() if 'tag' in key]!=[]:
        logging.error(f"Tags modification not implemented")
        sys.exit(1)

    if [val for key, val in conditions.items() if 'tag' in key]!=[]:
        logging.error(f"Modification by tag not implemented")
        sys.exit(1)


    # Normalize modifs
    try:
        modifs = normalize_link_infos(modifs)
    except:
        logging.error(f"Bad link modification")
        sys.exit(1)
    # Normalize conditions
    try:
        conditions = normalize_link_infos(conditions)
    except:
        logging.error(f"Bad link modif's conditions")
        sys.exit(1)

    # Prepare query
    ## Prepare modifs
    try:
        modifs = normalize_modif_to_str(modifs)
    except:
        logging.error(f"Can't prepare link modification")
        sys.exit(1)
    ## Prepare conditions
    try:
        conditions = normalize_conditions_to_str(conditions)
    except:
        logging.error(f"Can't prepare link modif's conditions")
        sys.exit(1)

    # Create the query
    query="UPDATE Link SET "+modifs+" WHERE "+conditions

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Edit values in Link table
        cur.execute(query)
        DB_connection.commit()
        logging.info(f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Link'")
    except mariadb.Error as e:
        logging.error(f"Modification failed -- SET {modifs}  WHERE {conditions} --  in the table 'Link' : {e}")
        sys.exit(1)
    

############################### LHS SECTION ###############################

def lhs(DB_connection, modifs, conditions):
    '''
    Edit Link_Hp_Serv table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    # Normalize modifs
    try:
        modifs = normalize_lhs_infos(modifs)
    except:
        logging.error(f"Bad lhs modification")
        sys.exit(1)
    # Normalize conditions
    try:
        conditions = normalize_lhs_infos(conditions)
    except:
        logging.error(f"Bad lhs modif's conditions")
        sys.exit(1)

    # Prepare query
    ## Prepare modifs
    try:
        modifs = normalize_modif_to_str(modifs)
    except:
        logging.error(f"Can't prepare lhs modification")
        sys.exit(1)
    ## Prepare conditions
    try:
        conditions = normalize_conditions_to_str(conditions)
    except:
        logging.error(f"Can't prepare lhs modif's conditions")
        sys.exit(1)

    # Create the query
    query="UPDATE Link_Hp_Serv SET "+modifs+" WHERE "+conditions

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Edit values in Link_Hp_Serv table
        cur.execute(query)
        DB_connection.commit()
        logging.info(f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Link_Hp_Serv'")
    except mariadb.Error as e:
        logging.error(f"Modification failed -- SET {modifs}  WHERE {conditions} --  in the table 'Link_Hp_Serv' : {e}")
        sys.exit(1)