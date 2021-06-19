'''
####### CAUTION ######
NOT IN USE:
Class to handle storage tools
'''

class Storage():
    def __init__(self, size, initVal):
        self.Size = size
        self.Array = []
        for i in range(size):
            self.append(initVal)
    
    def shift(self, val):
        for i in range(1,len(arr)):
            Array[-i] = Array[-(i+1)]
        Array[0] = val

    def getArray(self):
        return self.Array
