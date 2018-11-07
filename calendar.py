# this class does no Paxos negotiation or input validation;
# Paxos details are handled elsewhere
class Calendar:
    def __init__(self):
        self.events = []

    def schedule(self, name, day, start, end, participants):
        self.events.append(Event(name, day, start, end, participants))
        self.events.sort()
        print("User requested SCHEDULE")

    def cancel(self):
        print("User requested CANCEL")

    def view(self):
        print("User requested VIEW")

    def myview(self):
        print("User requested MYVIEW")

    def checkpoint():
        print("Save a copy of the calendar")

    def load():
        print("Loading the latest checkpoint into memory")
