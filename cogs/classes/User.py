import os

class User:
    def __init__(self, id, gift=None, recieve=None):
        self.id = id
        self.gift = gift
        self.recieve = recieve

    def getID(self):
        return self.id

    def setID(self, id):
        self.id = id
    
    def getGift(self):
        return self.gift
    
    def setGift(self, gift):
        self.gift = gift
    
    def getRecieve(self):
        return self.recieve

    def setRecieve(self, recieve):
        self.recieve = recieve