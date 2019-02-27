from interface import Interface
from threading import RLock
import socket
import select
import json
import random
import string
import AiguillageBuilder


class Client:

    previousIds = []

    def __init__(self, socket=None, name=None, id=None):
        self.sock = socket
        self.name = name
        self.id = id

    def generateNewId():
        while True:
            newId = ''.join(random.choices(string.ascii_uppercase, k=15))
            if newId not in Client.previousIds:
                return newId


class NetworkInterface(Interface):
    allowAiguillageHandling = True
    allowUserInteraction = True
    compatibleSinglePinMode = True
    id = 'NetworkInterface'

    def __init__(self, res):
        super().__init__()
        self.alimentations = []
        self.clients = []
        self.aiguillages = []

        self.eventList = []
        self.eventListLock = RLock()

        self.processList = []
        self.processListLock = RLock()
        self.res = res
        self.clients = []
        self.socketBuffers = {}

    def init(self):
        print('creating socket...')
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', 2121))
        self.serverSocket.listen(5)
        print('server is now listening on port 2121')

    def queue(self, *args):
        self.eventListLock.acquire()
        self.eventList.append(tuple(args))
        self.eventListLock.release()

    def sync(self, func, *args):
        self.processListLock.acquire()
        self.processList.append((func, tuple(args)))
        self.processListLock.release()

    def update(self):
        readSock = []
        readSock.append(self.serverSocket)
        for client in self.clients:
            readSock.append(client.sock)

        readable, writable, errored = select.select(readSock, [], [], 0.001)
        for loopSocket in readable:
            if loopSocket is self.serverSocket:
                client, adress = loopSocket.accept()
                print('> nouvelle connection entrante...')
                self.clients.append(Client(client))
            else:
                if loopSocket in self.socketBuffers:
                    self.socketBuffers[loopSocket] += loopSocket.recv(2048)
                    print(self.socketBuffers[loopSocket])
                else:
                    self.socketBuffers[loopSocket] = loopSocket.recv(2048)

                futureMessage = bytearray(self.socketBuffers[loopSocket])
                futureMessage = futureMessage.decode()
                del self.socketBuffers[loopSocket]

                message = None
                idHeader = futureMessage.find('[beginMsg=')
                key = ''
                if idHeader != -1:
                    key = futureMessage[idHeader + len('[beginMsg='):idHeader + len('[beginMsg=') + 10]
                idEnd = NetworkInterface.findStr(futureMessage, "[endMsg=")
                nextEndId = 0
                for it in idEnd:
                    endKey = futureMessage[it + len('[endMsg='):it + len('[endMsg=') + 10]
                    if endKey == key:
                        message = futureMessage[nextEndId + len('[]beginMsg=') + 10 - 1: it]
                        nextEndId = it + len('[]endMsg=') + 10 - 1
                        # self.socketBuffers[socket] = self.socketBuffers[socket][it + len('[]endMsg=') + 10 + 1:]
                        # futureMessage = futureMessage[it + len("endMsg[]=") + 10 + 1:]

                    if message is not None:
                        print("message : ", message)
                        message = json.loads(message)
                        client = None
                        for cl in self.clients:
                            if cl.sock == loopSocket:
                                client = cl

                        eventType = message['event_type']
                        print(eventType)

                        if eventType == "SendHeadMessage":
                            if message['wish_recover'] is True:
                                pass
                            else:
                                client.id = Client.generateNewId()
                                answer = {}
                                answer['event_type'] = 'Logged'
                                answer['is_recovered'] = False
                                answer['key'] = client.id
                                self.sendMessage(loopSocket, json.dumps(answer))

                        elif eventType == "GetAiguillages":
                            print('sending aiguillage data')
                            answer = {}
                            interfaces = self.res('interfaces')
                            aiguillagesList = []
                            interfaceId = 0
                            for interface in interfaces:
                                if interface.allowAiguillageHandling:
                                    for aiguillage in interface.aiguillages:
                                        toAdd = aiguillage.serialize()
                                        toAdd['aiguillage_handler_id'] = interfaceId
                                        aiguillagesList.append(toAdd)
                                        interfaceId += 1
                            answer['event_type'] = 'GotAiguillages'
                            answer['aiguillages'] = aiguillagesList
                            self.sendMessage(loopSocket, json.dumps(answer))

                        elif eventType == "SwitchAiguillage":
                            aiguillageHandlers = []
                            for interface in self.res('interfaces'):
                                if interface.allowAiguillageHandling:
                                    aiguillageHandlers.append(interface)
                            aiguillage = aiguillageHandlers[message['aiguillage_handler_id']].aiguillages[message['aiguillage_id']]
                            aiguillage.switch(message['target_direction'])

                        elif eventType == "GetFullData":
                            answer = {}
                            interfaces = self.res("interfaces")
                            interfaceId = 0
                            aiguillagesList = []
                            alimentationsList = []
                            for interface in interfaces:
                                if interface.allowAiguillageHandling:
                                    for aiguillage in interface.aiguillages:
                                        toAdd = aiguillage.serialize()
                                        toAdd["aiguillage_handler_id"] = interfaceId
                                        aiguillagesList.append(toAdd)

                                        if interface.compatibleSinglePinMode is True:
                                            for alimentation in interface.alimentations:
                                                toAdd = {}
                                                toAdd['coord'] = alimentation[0]
                                                print(toAdd['coord'])
                                                toAdd['alimentation'] = alimentation[1].serialize()
                                                toAdd['coord']["aiguillage_handler_id"] = interfaceId
                                                alimentationsList.append(toAdd)
                                interfaceId += 1

                            answer['event_type'] = "GotFullData"
                            answer['data'] = {}
                            answer["data"]['aiguillages'] = aiguillagesList
                            answer["data"]["alimentations"] = alimentationsList
                            self.sendMessage(loopSocket, json.dumps(answer))

                        elif eventType == "GetAiguillageBuilders":
                            answer = {}
                            answer["event_type"] = "GotAiguillageBuilders"
                            answer["data"] = AiguillageBuilder.AiguillageBuilder.getAiguillageBuilders()
                            self.sendMessage(loopSocket, json.dumps(answer))

                        elif eventType == "AddAiguillage":
                            print(message)

    def log(message):
        print('[DEBUG] NetworkInterface : ' + message)

    def save(self):
        return super().save()

    def restore(self, data):
        super().restore(data)

    def stop(self, message):
        print('closing network...')
        self.serverSocket.close()

    def findStr(string, substr):
        indexes = []
        index = -1
        while True:
            index = string.find(substr, index + 1)
            if index == -1:
                break
            else:
                indexes.append(index)
        return indexes

    def sendMessage(self, socket, message):
        key = ''.join(random.choices(string.ascii_uppercase, k=10))
        toSend = "[beginMsg=" + key + "]" + message + "[endMsg=" + key + "]"
        socket.send(bytes(toSend, 'utf-8'))

    def onAiguillageSwitched(self, aiguillage):
        print("[NETWORKINTERFACE]Aiguillage switched")
        for client in self.clients:
            answer = {}
            answer['event_type'] = "Dirty"
            self.sendMessage(client.sock, json.dumps(answer))
