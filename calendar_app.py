from sys import argv
from threading import Thread

from UdpServer import UdpServer
from calendar import Calendar


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

    return site_id, site_index, int(port), hosts

# -----------------------------------------------------------------------------
def parse_command(user_input, calendar):
    user_input = user_input.split()
    command = user_input[0]
    command = command.lower()
    args = user_input[1:]

    if command == "schedule":
        name, day, start, end = args[0:4]
        participants = args[4:]
        if len(participants) == 1:
            participants = participants[0].split(",")
        # proposer proposes a value
        # if successful add it to the schedule:
        
        calendar.schedule(name, day, start, end, participants)
    elif command == "cancel":
        # proposer proposes a value
        # if successful:
        calendar.cancel()
    elif command == "view":
        calendar.view()     # no proposals necessary    
    elif command == "myview":
        calendar.myview()   # no proposals necessary
    elif command == "log":
        print("User requested LOG")
    else:
        print("ERROR: Invalid command.")






# -----------------------------------------------------------------------------
def user_input():
    global running
    calendar = Calendar()
    
    while running:
        command = input("Enter a command: ")
        print(command)
        if command.lower() == "quit" or command == "exit":
            print("Exiting.")
            running = False
            break
        else:
            parse_command(command, calendar)


# -----------------------------------------------------------------------------
def server(site_id, port):
    global running

    docker = False
    if docker:
        print("This line should only print if you are running on Docker")
        server = UdpServer(site_id, port, 1.0)
    else:
        print("Not running on Docker - using ip = 127.0.0.1")
        server = UdpServer("127.0.0.1", port, 1.0)   # else use this line

    while running:
        # attempt to receive any message
        data, address = server.receive()
        # print("Receive timed out")


# =============================================================================
running = True

if __name__ == "__main__":
    site_id, site_index, port, hosts = read_known_hosts()
    print(site_id, site_index, port, hosts)

    t1 = Thread(target=user_input, args=())
    t2 = Thread(target=server, args=(site_id, port))

    t1.start()
    t2.start()
    t1.join()
    t2.join()