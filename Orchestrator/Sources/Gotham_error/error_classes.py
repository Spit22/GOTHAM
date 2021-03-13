import json
# Logging comiponents
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def format_error(error_title, debug_information, debug_mode):
    # error_title (String) : The error name, principally the source (i.e error in port edition)
    # debug_informaiton (String) : All errors concatenated from original error, separated by '-', and usefull for debugging
    # debug_mode (Bool) : True if you want to return debug_information, False in the other case
    # Return a json object containing error information like {"error": "An error occured in port edition", "debug":"str can't be a NULL - variable referenced before asssigment - not a valid RSA key file"}

    error = {}
    error["error"] = str(error_title)
    
    if debug_mode:
        error["debug"] = str(debug_information)

    # Return the formatted error
    return json.dumps(error)
