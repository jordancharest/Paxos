class Event:
    def __init__(self, name=None, date=None, start=None, end=None, participants=None):
        self.date = date
        self.start = start
        self.end = end
        self.name = name
        self.participants = participants
        if not isinstance(participants, list):
            self.participants = [self.participants]
                    

    def __lt__(self, other):
        return ((self.date < other.date) or
               (self.date == other.date and self.start < other.start) or
               (self.date == other.date and self.start == other.start and self.name < other.name))

    def __repr__(self):
        result = self.name + " " + self.date + " " + self.start + " " + self.end + " "
        result += ",".join(self.participants)
        return result
        
    def load(event_str):
        name,date,start,end,participants = event_str.split(" ")
        participants = participants.split(",")
        e = Event(name, date, start, end, participants)
        return e
