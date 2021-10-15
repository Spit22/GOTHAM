import subprocess


def main(hostname):
    '''
    Check if a host is alive on the network

    ARGUMENTS:
        hostname (string) : ip or hostname of the checked server

    Return True if server is alive, False in the other case
    '''
    try:
        subprocess.check_call(
            ['ping', '-c 1', hostname],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return True
    except BaseException:
        return False
