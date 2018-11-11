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
        self.server = server

    def propose(self, event, new_or_cancel, participants=None):
        msg = {
            "kind" : "prepare",
            "proposal_num" : self.proposal_num,
        }

        # try to send prepare message three times
        attempts = 0
        try_again = True
        while try_again and attempts < 3:
            promised, try_again = self.send_to_acceptors(msg)
            attempts += 1
            if try_again:
                self.proposal_num += 1000

        # if prepared, continue with the protocol - send accept messages
        acknowledged = False
        if promised:
            print("Received promises from majority, now sending accept messages")
            msg = {
                    "new_or_cancel" : new_or_cancel,
                    "kind" : "accept",
                    "proposal_num" : self.proposal_num,
                    "event" : event,
                    "participants" : participants
            }
            acknowledged, _ = self.send_to_acceptors(msg)

        # if acknowledged by majority, send commit messages
        accepted = False
        if acknowledged:
            print("Received acknowledgement from majority")
            msg = {
                "new_or_cancel" : new_or_cancel,
                "kind" : "commit",
                "proposal_num" : self.proposal_num,
                "event" : event,
                "participants" : participants
            }
            accepted = True
            self.send_commit(msg)

        # reset the proposal number
        self.proposal_num = self.port

        return accepted

    def send_to_acceptors(self, msg):
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
        while (received < len(self.sites)) and (time.time() - start < config.paxos_timeout):
            data, address = self.server.receive()
            if data:
                kind = data["kind"]
                # message from acceptor to continue
                if kind == "promise" or kind == "acknowledge":
                    received += 1

                # message from acceptor meaning proposal number is too small
                elif kind == "failure":
                    received += 1
                    return False, True  # not accepted, try again (larger proposal number)

                # message from acceptor to abort
                elif kind == "abort":
                    abort = True
                    break

                # this is a message from another proposer, handle immediately
                elif kind == "prepare" or kind == "accept" or kind == "commit":
                    self.accept(data)

                else:
                    print("Unknown message type.")
        config.mutex.release()

        if abort:
            print("Received abort")
            return False, False # not accepted, don't try again

        # if we didn't receive a response from the majority
        elif received < ceil(len(self.sites)/2.0):
            print("Didn't get responses from majority")
            return False, True  # not accepted, try again

        # else we received a response from majority and no aborts (continue with protocol)
        else:
            return True, False  # accepted, don't try again


    def send_commit(self, msg):
        config.mutex.acquire()
        for site_id, port in self.sites:
            self.server.send(msg, (site_id, port))
        config.mutex.release()


    def accept(self, msg, address):
        kind = msg["kind"]
        accept_num = msg["proposal_num"]
        print("Received {0} message with proposal number {1}".format(kind, accept_num))

        # this may happen if the proposer gives up early due to receiving an abort
        # if it does, just ignore it
        if kind == "promise" or kind == "failure" or kind == "abort":
            print("Ignoring message")
            return

        if kind == "prepare":
            # check if the proposal number is high enough
            if accept_num < self.max_accepted:
                # send message saying need higher proposal number
                response = {
                    "kind" : "failure"
                }

            else:
                self.max_accepted = accept_num
                print("New max accepted is {}. Sending promise message".format(self.max_accepted))
                response = {
                    "kind" : "promise"
                }

            self.server.send(response, address)

        elif kind == "accept":
            # if there's a conflict, send abort and send the conflicting event so that the other
            # process can add it to their calendar
            conflicting_event = config.calendar.check_conflict(msg["event"], msg["new_or_cancel"])
            if conflicting_event != None:
                print("Conflict in the schedule. Sending abort")
                response = {
                    "kind" : "abort",
                    "conflict" : conflicting_event
                }

            # verify that the proposal number is equal to the max accepted
            # send message saying there's a new higher proposal number
            elif msg["proposal_num"] != self.max_accepted:
                print("Previously promised but have now promised to a higher proposal number")
                response = {
                    "kind" : "failure"
                }

            # everything checks out, send acknowledgement message
            else:
                print("Acknowledging the acceptance. Waiting for commit to save event.")
                response = {
                    "kind" : "acknowledge"
                }
            
            self.server.send(response, address)

        # paxos fully executed, record event in the log
        elif kind == "commit":
            # record event
            if msg["new_or_cancel"] == "new":
                print("Adding event to calendar and recording in log")
                config.calendar.schedule(msg["event"])
            elif msg["new_or_cancel"] == "cancel":
                print("Canceling event")
                config.calendar.cancel(msg["event"])

            self.max_accepted = -1