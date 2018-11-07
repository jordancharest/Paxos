from sys import argv
from threading import Thread

# -----------------------------------------------------------------------------
def read_known_hosts():
    """
    Read all hosts from text file and ensure that the given site ID is in
    the group of known hosts. Otherwise other sites will not know of this
    site's existence.
    """
    if len(argv) == 2:
        _, site_id = argv
        
        # read all known hosts
        file = open("knownhosts_udp.txt", "r")
        hosts = []
        if file.mode == "r":
            for line in file:
                IP, port = line.split()
                hosts.append((IP, int(port)))
            
        # ensure our site ID is in the group of known hosts
        #  and find the index of the host
        site_index = 0
        for host in hosts:
            if host[0] == site_id:
                ip = host[0]
                port = host[1]
                break
            site_index += 1
        else:
            print("Site ID must be contained in knownhosts_udp.txt")
            exit()

    else:
        print("Invalid Argument(s)")
        print("USAGE: {0} <site-id>".format(sys.argv[0]))
        exit()

    return site_id, site_index, ip, int(port), hosts


# -----------------------------------------------------------------------------
def parse_command():
    pass




# -----------------------------------------------------------------------------
def user_input():
    global running
    print("User Input Thread")
    while running:
        command = input("Enter a command: ")
        print(command)
        if command.lower() == "quit" or command == "exit":
            print("Exiting.")
            running = False
            break
        else:
            calendar = parse_command()


# -----------------------------------------------------------------------------
def server():
    global running
    print("Server Thread")
    i = 0
    while running:
        if i % 100000000 == 0:
            print("still running")
        i += 1


# =============================================================================
running = True

if __name__ == "__main__":
    site_id, site_index, ip, port, hosts = read_known_hosts()
    print(site_id, site_index, ip, port, hosts)

    t1 = Thread(target=user_input, args=())
    t2 = Thread(target=server, args=())

    t1.start()
    t2.start()

    t1.join()
    t2.join()
