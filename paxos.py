# Paxos worker class acts as both a Proposer and an Acceptor!

class Worker:
    def __init__(self, ID, sites, port):
        self.sites = sites
        self.ID = ID
        self.proposal_num = port

    def propose_new(self, event):


        return True

    def propose_cancellation(self, event_name, participants):
        




        return True

    def accept(self):
        pass

