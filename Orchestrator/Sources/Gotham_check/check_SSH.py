#from gotham_server_communication import main
from io import StringIO
from Gotham_SSH_SCP import execute_commands

def main(ip, ssh_port, used_ssh_key):
    # Cette fonction retourne True si la connexion SSH peut être établie, False sinon.
    #
    # ip (string) : ip du serveur à tester
    # ssh_port (int) : port du service ssh à utiliser
    # used_ssh_key (string) : clé privée à utiliser pour l'auth
    #
    # Déclaration des variables locales
    command_exec_check = ["echo 'alive' > /tmp/gotham_status && rm -rf /tmp/gotham_status"]
    # On essaie d'exécuter la commande sur le serveur distant
    try:
        execute_commands(ip, ssh_port, used_ssh_key, command_exec_check)
    except:
        # Si c'est pas possible, return False
        return False
    # Si tout s'est passé, True
    return True
