# -*- coding: utf-8 -*-
from interfaces.DirectAiguillageHandler import DirectAiguillageHandler
import time
from interfaces.DirectConsoleHandler import ConsoleUserHandler
from pinHandler import gpio
import pickle
from interfaces.NetworkInterface import NetworkInterface


version = 'P0.1a'
interfaces = []

mustStop = False


def isStopping():
    return mustStop


def stop(args):
    for linterface in interfaces:
        linterface.unsuscribe('stop', stop)
    global mustStop
    mustStop = True


def save(args):
    f = open('save', 'wb')
    toSave = []
    for interface in interfaces:
        toSave.append(interface.save())
    pickle.dump(toSave, f)


def restore(args):

    saved = pickle.load(open('save', 'rb'))
    count = 0
    for interface in interfaces:
        interface.restore(saved[count])
        count += 1


def res(type):
    if type == 'aiguillages':
        aiguillagesList = []
        for interface in interfaces:
            if interface.allowAiguillageHandling is True:
                for aiguillage in interface.aiguillages:
                    aiguillagesList.append((interface, aiguillage))
        return aiguillagesList
    elif type == 'interfaces':
        return interfaces


def aiguillageSwitched(aiguillage):
    for interface in interfaces:
        interface.onAiguillageSwitched(aiguillage)


gpio.init()

interfaces.append(DirectAiguillageHandler(res))
interfaces.append(ConsoleUserHandler(res))
interfaces.append(NetworkInterface(res))

# interfaces[1].subscribe('stop', None, stop)
print(interfaces)
for linterface in interfaces:
    linterface.subscribe('stop', None, stop)
    linterface.subscribe('save', None, save)
    linterface.subscribe('restore', None, restore)
    linterface.subscribe('aiguillageSwitched', None, aiguillageSwitched)

    linterface.init()

for linterface in interfaces:
    linterface.launch()

# Main loop
while isStopping() is not True:
    for interface in interfaces:
        interface.update()
        time.sleep(0.001)
