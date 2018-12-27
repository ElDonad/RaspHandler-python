import random

class EventObj:
    __nextId = 0

    def __init__(self):
        self.__subscribers = {}

    def getNewId():
        EventObj.__nextId += 1
        return EventObj.__nextId - 1

    def subscribe(self, eventName, target, func):
        print('tip' + eventName + str(self))
        newId = EventObj.getNewId()
        self.__subscribers[newId] = (eventName, target, func)
        return newId

    def unsuscribe(self, eventName, func):
        idToDelete = None
        for id, event in self.__subscribers.items():
            if event[0] == eventName and event[2] == func:
                idToDelete = id
        if idToDelete != None:
            print('coucou'  +str(len(self.__subscribers)))
            del self.__subscribers[idToDelete]
            
    def emit(self, eventName, args):
        for value, sub in self.__subscribers.items():
            if (sub[0] == eventName):
                target = sub[1]
                if target != None:
                    sub[2](target, args)
                else:
                    sub[2](args)
