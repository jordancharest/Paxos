from sys import argv
from threading import Thread

from UdpServer import UdpServer
from calendar import Calendar
from paxos import Worker
from event import Event



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
    global worker

    user_input = user_input.split()
    command = user_input[0]
    command = command.lower()
    args = user_input[1:]

    # proposer proposes a new event
    # if successful, add it to the calendar
    if command == "schedule":
        # first verify this site is a participant in the new event
        event_string = " ".join(args)
        event = Event.load(event_string)
        if worker.ID not in event.participants:
            print("You cannot schedule an event for other users")
            return

        # propose the new event
        accepted = worker.propose_new(event)
        if accepted:
            calendar.schedule(event)

    # proposer proposes an event cancellation
    # if successful, remove it from the calendar
    elif command == "cancel":
        # first verify that the event exists and this site is a participant
        event_name = args[0]
        participants = calendar.get_participants(event_name)
        if participants == None:
            return

        # propose the event cancellation
        accepted = worker.propose_cancellation(event_name, participants)
        if accepted:
            calendar.cancel(event_name)

    # view the entire calendar
    elif command == "view":
        calendar.view()

    # view all events this site is particpating in  
    elif command == "myview":
        calendar.myview()

    # view the log
    elif command == "log":
        print("User requested LOG")

    # all other commands are invalid
    else:
        print("ERROR: Invalid command.")



# -----------------------------------------------------------------------------
def user_input(site_id, sites, port):
    global running
    global worker

    calendar = Calendar(site_id)
    
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
    global worker

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

# all threads need access to these resources
running = True
worker = None

if __name__ == "__main__":
    site_id, site_index, port, sites = read_known_hosts()
    print(site_id, site_index, port, sites)
    worker = Worker(site_id, sites, port)

    # one thread to run the server, one for user input
    t1 = Thread(target=user_input, args=(site_id, sites, port))
    t2 = Thread(target=server, args=(site_id, port))

    t1.start()
    t2.start()
    t1.join()
    t2.join()