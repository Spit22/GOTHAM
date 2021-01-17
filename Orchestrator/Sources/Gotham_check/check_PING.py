import subprocess

def main(hostname):
    try:
        subprocess.check_call(['ping', '-c 1', hostname], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True
    except:
        return False