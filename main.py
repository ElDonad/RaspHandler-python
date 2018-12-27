# -*- coding: utf-8 -*-


version = 'P0.1a'

from AiguillageHandler import AiguillageHandler
from interfaces.DirectAiguillageHandler import DirectAiguillageHandler
from aiguillage import Aiguillage
from aiguillage import *
import time
from interfaces.DirectConsoleHandler import ConsoleUserHandler
from pinHandler import gpio
import pickle
from interfaces.NetworkInterface import NetworkInterface

interfaces = []

mustStop = False
def isStopping():
    return mustStop


def stop(args):
    print("stop demandé")
    for interface in interfaces:
        interface.unsuscribe('stop', stop)
        interface.stop('parce que')
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
            if interface.allowAiguillageHandling == True:
                print('interface found !')
                for aiguillage in interface.aiguillages:
                    aiguillagesList.append((interface, aiguillage))
        return aiguillagesList
    elif type == 'interfaces':
        return interfaces

gpio.init()

interfaces.append(DirectAiguillageHandler(res))
interfaces.append(ConsoleUserHandler(res))
interfaces.append(NetworkInterface(res))

#interfaces[1].subscribe('stop', None, stop)
print(interfaces)
for linterface in interfaces:
    linterface.subscribe('stop', None, stop)
    linterface.subscribe('save', None, save)
    linterface.subscribe('restore', None, restore)
    print('top')

    linterface.init()

for linterface in interfaces:
    linterface.launch()

#Main loop
while isStopping() != True:
    for interface in interfaces:
        interface.update()
        time.sleep(0.001)
