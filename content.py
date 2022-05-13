import config as cf
import numpy as np


class Content(object):
    def __init__(self, _title, _size):
        self.title = _title
        self.size = _size

class contentStorage(object):
    def __init__(self, _size):
        self.capacity = _size
        self.stored = 0
        self.storage=[]

    def abletostore(self,c:Content):
        freeSpace = self.capacity-self.stored
        if(freeSpace>=c.size):
            return 1
        else:
            return 0 

    def addContent(self,c:Content):
        self.storage.append(c)
        self.stored = self.stored + c.size

    def isstored(self,c:Content):
        if len(self.storage)>0:
            for i in self.storage:
                if i.title == c.title:
                    return 1
        return 0
        
    def delcontent(self,c:Content):
        newstorage=[]
        for i in self.storage:
            if i is c:
                self.stored = self.stored-c.size
            else:
                newstorage.append(i)
        self.storage=newstorage

#def count_redundancy(contentList:list,self):
