class EventObj:
    __nextId = 0

    def __init__(self):
        self.subscribers = {}

    def getNewId():
        EventObj.__nextId += 1
        return EventObj.__nextId - 1

    def subscribe(self, eventName, target, func):
        newId = EventObj.getNewId()
        self.subscribers[newId] = (eventName, target, func)
        return newId

    def unsuscribe(self, eventName, func):
        idToDelete = None
        for id, event in self.subscribers.items():
            if event[0] == eventName and event[2] == func:
                idToDelete = id
        if idToDelete is not None:
            del self.subscribers[idToDelete]

    def emit(self, eventName, args):
        emitters = []
        for value, sub in self.subscribers.items():
            if sub[0] == eventName:
                emitters.append((sub[1], sub[2]))
        for emitter in emitters:
            if emitter[0] is None:
                emitter[1](args)
            else:
                emitter[1](emitter[0], args)
