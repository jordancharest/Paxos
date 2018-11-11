# this class does no Paxos negotiation
# Paxos details are handled elsewhere
from event import Event

class Calendar:
    def __init__(self, ID):
        self.events = []
        self.ID = ID

    def schedule(self, event):
        self.events.append(event)
        self.events.sort()

    def cancel(self, event_name):
        # modify the event list to remove the meeting
        self.events = [event for event in self.events if event.name != event_name]


    def get_participants(self, event_name):
        participants = []
        for e in self.events:          
            if e.name == event_name:
                if self.ID in e.participants:
                    return e.participants
                else:
                    return None
        print("Event doesn't exist.")
        return None

    def check_conflict(self, event, kind):
        conflicting_event = None
        if kind == "new":
            # check that the time slot is available
            print("checking that the time slot is available for a new event")

        elif kind == "cancel":
            # check that the event hasn't already been cancelled
            print("Checking that the event is in the calendar so we can cancel it")

        return conflicting_event


    def view(self):
        print("User requested VIEW")
        for e in self.events:
            print(e)

    def myview(self):
        print("User requested MYVIEW")
        for e in self.events:
            if self.ID in e.participants:
                print(e)

    def checkpoint():
        print("Save a copy of the calendar")

    def load_checkpoint():
        print("Loading the calendar from log")

    def load():
        print("Loading the latest checkpoint into memory")
