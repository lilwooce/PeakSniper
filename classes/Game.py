import os

class Game:
    def __init__(self, id, players):
        self.id = id
        self.players = players

    def getID(self):
        return self.id
    
    def getPlayers(self):
        return self.players
    
    def getPlayer(self, id):
        for plr in self.players:
            if plr.getID() == id:
                return plr

    def getReciever(self, gift):
        for plr in self.players:
            if plr.getRecieve() == gift:
                return plr