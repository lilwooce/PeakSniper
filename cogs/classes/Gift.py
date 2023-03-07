import os

class Gift:
    def __init__(self, text, image=None, stolen=0):
        self.text = text
        self.image = image
        self.stolen = stolen
    
    def getText(self):
        return self.text
    
    def getImage(self):
        return self.image
    
    def getStolen(self):
        return self.stolen
    
    def setStolen(self, stolen):
        self.stolen = stolen
    
    def canSteal(self):
        if self.stolen < 3:
            return True
        return False