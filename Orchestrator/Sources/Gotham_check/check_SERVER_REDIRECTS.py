import socket


def main(ip_srv, port):
    # Check if requesing ip_serv:exposed_port is open
    #
    # ip_srv (string): ip of the server we want to test
    # exposed_port (int): port we want to test
    #
    # Return True if port is open, False in the other case
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip_srv, int(port)))
    if result == 0:
        return True
    sock.close()
    return False


if __name__ == '__main__':
    main("172.16.2.201", 8081)
