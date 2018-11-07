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
        print("User requested SCHEDULE")

    def cancel(self, event_name):
        print("User requested CANCEL")
        # modify the event list to remove the meeting
        self.events = [event for event in self.events if event.name != event_name]


    def get_participants(self, event_name):
        participants = []
        for e in self.events:          
            if e.name == event_name:
                if self.ID in e.participants:
                    return e.participants
                else:
                    print("You are not participating in that event")
                    return None
        print("Event doesn't exist.")
        return None           




    def view(self):
        print("User requested VIEW")
        for e in self.events:
            print(e)

    def myview(self):
        print("User requested MYVIEW")
        for e in self.events:
            for p in e.participants:
                if self.ID in p:
                    print(e)
                    break

    def checkpoint():
        print("Save a copy of the calendar")

    def load():
        print("Loading the latest checkpoint into memory")
