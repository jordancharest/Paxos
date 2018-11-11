# Paxos worker class acts as both a Proposer and an Acceptor!
import config
import json
import time
from math import ceil

from event import Event



# TODO:
#   - verify that the proposal number of this process is the highest that
#       this process has seen so far


class Worker:
    def __init__(self, ID, sites, port, server=None):
        self.ID = ID
        self.port = port
        self.sites = [site for site in sites if site[0] != self.ID]
        self.proposal_num = port
        self.max_accepted = -1

    def propose_new(self, event):
        msg = {
            "new_or_cancel" : "new",
            "kind" : "prepare",
            "proposal_num" : self.proposal_num,
            "event" : event
        }

        # try three times
        attempts = 0
        majority = False
        while not majority and attempts < 3:
            accepted, majority = self.propose(msg)
            self.proposal_num += 1000
            attempts += 1

        # reset the proposal number
        self.proposal_num = self.port

        return accepted

    def propose_cancellation(self, event_name, participants):
        msg = {
            "new_or_cancel" : "cancel",
            "kind" : "prepare",
            "proposal_num" : self.proposal_num,
            "event" : event_name
        }

        # try three times
        attempts = 0
        majority = False
        while not majority and attempts < 3:
            print("Attempt ", attempts)
            accepted, majority = self.propose(msg)
            self.proposal_num += 1000
            attempts += 1

        # reset the proposal number
        self.proposal_num = self.port

        return accepted


    def propose(self, msg):
        # send all messages
        # don't let the other thread accept messages for a brief moment
        # this thread will handle acceptances while proposal is running
        config.mutex.acquire()
        for site_id, port in self.sites:
            self.server.send(msg, (site_id, port))

        # receive all messages or timeout
        received = 0
        abort = False
        start = time.time()
        while (received < len(self.sites)) and (time.time() - start < config.timeout):
            data, address = self.server.receive()
            if data:
                # message from acceptor to continue
                if data["kind"] == "promise" or data["kind"] == "failure":
                    received += 1

                # message from acceptor to abort
                elif data["kind"] == "abort":
                    abort = True
                    break

                # this is a message from another proposer, handle immediately
                elif data["kind"] == "prepare" or data["kind"] == "commit":
                    self.accept(data)
        config.mutex.release()

        # if we didn't receive a response from the majority
        if received < ceil(len(self.sites)/2.0):
            return False, False

        # not accepted, but a majority responded - to break the loop,
        # even if a majority didn't respond
        elif abort:
            return False, True
        

    def accept(self, msg):
        kind = msg["kind"]
        accept_num = msg["proposal_num"]
        print("Received {0} message with proposal number {1}".format(kind, accept_num))

        # this may happen if the proposer gives up early due to receiving an abort
        # if it does, just ignore it
        if kind == "promise" or kind == "failure" or kind == "abort":
            return

        if kind == "prepare":
            # check if the proposal number is high enough
            if accept_num < self.max_accepted:
                # send message saying need higher proposal number
                pass

            # next check for conflicts
            conflict = config.calendar.conflict_check(msg["event"])
            if conflict:
                # send message saying to abort
                pass

        elif kind == "accept":
            # verify that the proposal number is equal to the max accepted
            if msg["proposal_num"] != self.max_accepted:
                # send message saying there's a new higher proposal number
                pass

        # paxos fully executed, record event in the log
        elif kind == "commit":
            # record event
            pass