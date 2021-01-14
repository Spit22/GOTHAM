#from gotham_server_communication import main
from io import StringIO
from Gotham_SSH_SCP import send_file_and_execute_commands
import os

Gotham_home = os.environ.get("GOTHAM_HOME")
print(Gotham_home)

# the data
ip = "172.16.2.201"
ssh_port = "22"
used_ssh_key = StringIO("""-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEAsqQkDR6tZ0S7Ipdt2Ccgf560exoDUoJ/wgocaJndSz9g94jHitCo
9LHSQkkatru0HK17ouZ/9os1a7I7GX0FnpIk4p2tiARMcG++aP0x8wUquDdnTFTqxSjVP3
CIzKZ8a0G0/4tI/EFKyF80n8WyGTMvfl0NRt2GgCXMiUupthIZp803DfPTV20IGWJqbHn2
/0HmyVCAiCpuT9R6Vg2ry/UVTQ4e7UijQuBEw7ZJPcwM0UhSdYSjIfTWu4R9dFJC2Rf2IH
dOGHHIpVYXSZcWlGaHKO8iPdCUMF185PsWW9Bo4neratqQYTgVOnzF50415FNjiKsYn1xr
0OlTPkPgCwAAA9BrSSAoa0kgKAAAAAdzc2gtcnNhAAABAQCypCQNHq1nRLsil23YJyB/nr
R7GgNSgn/CChxomd1LP2D3iMeK0Kj0sdJCSRq2u7QcrXui5n/2izVrsjsZfQWekiTina2I
BExwb75o/THzBSq4N2dMVOrFKNU/cIjMpnxrQbT/i0j8QUrIXzSfxbIZMy9+XQ1G3YaAJc
yJS6m2EhmnzTcN89NXbQgZYmpsefb/QebJUICIKm5P1HpWDavL9RVNDh7tSKNC4ETDtkk9
zAzRSFJ1hKMh9Na7hH10UkLZF/Ygd04YccilVhdJlxaUZoco7yI90JQwXXzk+xZb0Gjid6
tq2pBhOBU6fMXnTjXkU2OIqxifXGvQ6VM+Q+ALAAAAAwEAAQAAAQAqATKA6z+20pB2F8k6
VCjuGTEy6PDzC8BireH0Lom8UdDJI55X46x2rQFVmL7xTL2TKK+zpCNeo2kSQ7xlx+H0YU
TPDGhrXSdkIMJTCYYfMI3U9yIQ7r6tUWajHiDsjhEfXzniBKxKtEeTSd+j2eaAympWeibP
DPO9WiX3+pSTPNVAuncx7fN8eSNzUr3DsOfB1GP/Xb/MEO+SAU5WVW8B4I/L1oBXggTUle
NxrYiyFGMH/bmPOeXEUJ7pP4ckxPKDde+wUgDA9t9atxrei1BFqmMb77AQKahD+CW8UYca
LdkUEpIioPE+W88dq1sa596L9ZnXVfulJjB9TtOHfy0RAAAAgQCQH6+xHnJc7fVe5FCD9c
qObxrjbLgZlFQSIFXODaQTRLFjhLHaPTeytJsCOcsd0hTaWPWTU4bVQoi2d93rLto11XCt
9XYgrtdzNg9Gf8YLgYS387YhmA5lKPirXvFKwut7RteIhOU49QKsg9GVaM7jHh4p/qHEqp
MjP6c7RzVqrwAAAIEA7AB/6Y6pgoNwxAmd9f8ARVRyIsi0HtbVOVuzim1omvYg6uW46XEB
3DFCTONHAgEey8xotUXte31h2+/9poaUMzvII1/7FQKvQ59NdVzgkbyEM/E6QdxbC2DDHm
kmwHrxrjlYDnoeQFnetyLiPcCCUbUO9cvXFKBk87xmKrhWeBcAAACBAMHHVfFKcXb2qYDS
oUBSyM/01bc/eiPuH2vb9ZsXQ3YM9N1ZCoQHlWp+UWI82dNBHGgvbCF5BvDq30cMioVjn7
SBGJ38bbgOOVPbbnD9Y5NHrQTeBL/0lbj13x3rYOu6lC8mQV3K6E4L+65n966wO5p+eUKQ
AqXAI/8umwAEK9wtAAAAFHZhZ3JhbnRAZGViaWFuMTAtbm1zAQIDBAUG
-----END OPENSSH PRIVATE KEY-----""")

def deploy(ip, ssh_port, used_ssh_key):
    # Déclaration des variables globales
    installNginx_file = "/data/scripts/install_nginx.sh"
    installNginx_dest = "/tmp/"
    command_exec_install = ["sh /tmp/install_nginx.sh"]
    # On copie et exécute le script d'install nginx sur le serveur
    send_file_and_execute_commands(ip, ssh_port, used_ssh_key, installNginx_file, installNginx_dest, command_exec_install)

if __name__ == '__main__':
    deploy(ip, ssh_port, used_ssh_key)
