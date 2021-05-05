#===Import GOTHAM's libs===#
from . import syslog_output
#==========================#


def syslog(hostname, syslog_port, protocol):
    '''
    Create a syslog output

    ARGUMENTS:
        hostname (string) : hostname of the remote syslog server
        port (string) : syslog port of the remote syslog server
    '''
    try:
        syslog_output.main(hostname, syslog_port)
    except Exception as e:
        error = "Fail to create syslog output"
        raise ValueError(error)

    