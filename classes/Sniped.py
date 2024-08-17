import os

class Sniped:
    def __init__(self, message, server, timestamp, sender):
        self.message = message
        self.server = server
        self.timestamp = timestamp
        self.sender = sender

    def getMessage(self):
        return self.message
    
    def getServer(self):
        return self.server
    
    def getTimestamp(self):
        return self.timestamp
    
    def getSender(self):
        return self.sender
    
    def setMessage(self, message):
        self.message = message
    
    def setServer(self, server):
        self.server = server
    
    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
    
    def setSender(self, sender):
        self.sender = sender
        