from . import error_classes


def format_usererror(error_title, debug_informations, debug_mode):
    # Format error before returning the to user
    #
    # error_title (String) : The error name, principally the source (i.e error in port edition)
    # debug_informaiton (String) : All errors concatenated from original error, separated by '-', and usefull for debugging
    # debug_mode (Bool) : True if you want to return debug_information, False in the other case
    #
    # Return a json string containing error information like {"error": "An error occured in port edition", "debug":"str can't be a NULL - variable referenced before asssigment - not a valid RSA key file"}

    # Get the json formated error
    error = error_classes.format_error(
        error_title, debug_informations, debug_mode)
    # Return the error
    return error
