# Paxos worker class acts as both a Proposer and an Acceptor!

class Worker:
    def __init__(self, ID, sites, port):
        self.sites = sites
        self.ID = ID
        self.proposal_num = port

    def propose_new(self, args):
        name, day, start, end = args[0:4]
        participants = args[4:]
        if len(participants) == 1:
            participants = participants[0].split(",")

        return True

    def propose_cancellation(self, event_name, participants):
        




        return True

    def accept(self):
        pass

