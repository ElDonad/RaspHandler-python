from interface import Interface
import threading
from threading import RLock
import asyncore
import socket

class Client:
    sock = None
    name = None
    id = None
    def __init__(self, socket=None, name=None, id=None):
        self.sock = socket
        self.name = name
        self.id = id


class NetworkInterface(Interface, asyncore.dispatcher):
    allowAiguillageHandling = True
    allowUserInteraction = True
    compatibleSinglePinMode = True
    id='NetworkInterface'



    def __init__(self, res):
        super().__init__()
        self.alimentations = []
        self.clients = []

        self.eventList = []
        self.eventListLock = RLock()

        self.processList = []
        self.processListLock = RLock()

        asyncore.dispatcher.__init__(self)
        self.res = res
        self.clients = []

    def init(self):
        print('creating socket...')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', 2121))
        NetworkInterface.log("after binding")
        self.listen(2121)
        NetworkInterface.log('After listening')
        self.loopThread = threading.Thread(target=asyncore.loop, name='asyncore loop', args=[0.01])
        self.loopThread.start()

    def queue(self, *args):
        self.eventListLock.acquire()
        self.eventList.append(tuple(args))
        self.eventListLock.release()

    def sync(self, func, *args):
        self.processListLock.acquire()
        self.processList.append((func,tuple(args)))
        self.processListLock.release()

    def handle_accept(self):
        NetworkInterface.log('accepting new client...')
        newSocket, adress = self.accept()
        self.clients.append(Client(socket=newSocket))

    def update(self):
        self.processListLock.acquire()
        self.eventListLock.acquire()
        for event in self.eventList:
            self.emit(*event)

        for process in self.processList:
            process[0](*(process[1]))

        self.processList = []
        self.eventList = []

        self.processListLock.release()
        self.eventListLock.release()

    def log(message):
        print('[DEBUG] NetworkInterface : ' + message)

    def save(self):
        return super().save()
    def restore(self, data):
        super().restore(data)

    def stop(self, message):
        print('closing network...')
        self.close()
