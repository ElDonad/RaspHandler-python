# -*- coding: utf-8 -*-

from interface import Interface
from threading import Thread, RLock
import threading
import time
import readchar
from aiguillage import Aiguillage, Direction, AlimentationState, PinState
from AiguillageHandler import AiguillageHandler, Alimentation
from AiguillageBuilder import AiguillageBuilder

allowUserInteraction = False
allowAiguillageHandling = True

class ProgrammStoppedExcept(Exception):
    def __init__(self, message):
        self.message = message

class ConsoleUserHandler(Interface):
    id = 'ConsoleUserHandler'

    def stop(self, reason="Le programme c'est arrêté normalement"):
        self.isStopping = True

    def update(self):
        self.processListLock.acquire()

        for process in self.processList:
            if process[0] == 'event':

                self.emit(*process[1])
            elif process[0] == 'process':
                process[1][0](*process[1][1])

        self.processList[:] = []

        self.processListLock.release()

    class ConsoleThread(Thread):
        def __init__(self, parent, isStopping):
            Thread.__init__(self)
            self.parent = parent
            self.isStopping = isStopping

            charsFile = open('chars.txt', 'r')
            chars = charsFile.read()
            self.enter = chars[0]
            self.backspace = chars[1]

        def queue(self, *event):
            self.parent.processListLock.acquire()
            self.parent.processList.append(('event',tuple(event)))
            self.parent.processListLock.release()

        def sync(self, func, *args):
            self.parent.processListLock.acquire()
            self.parent.processList.append(('process',(func, tuple(args))))
            self.parent.processListLock.release()

        def run(self):
            try:
                while(self.parent.isStopping == False):
                    print("\n \n \n +++ RaspHandler v.P0.1a +++")
                    print("1. run a new instance")
                    print("2. restore previous instance \n")
                    truc = self.safeInput()
                    run = False
                    if truc == '2':
                        self.queue('restore', None)
                        run = True
                    elif truc == '1':
                        print ('> Running new instance... \n')
                        run = True
                    while(run == True and self.parent.isStopping == False):
                        print('\n++ Menu principal ++')
                        print("1. consulter la liste des aiguillages")
                        print("2. ajouter ou supprimer des aiguillages")
                        print("3. Gestionnaire d'alimentation")
                        print("4. Manipuler les aiguillages")
                        print("s. sauvegarder")
                        truc = self.safeInput()
                        if truc == "1":
                            self.displayAiguillageList()
                            continue

                        elif truc=="3":
                            print("\n+ Gestionnaire d'alimentation : +")
                            print("1. consulter la liste des alimentations")
                            print("2. ajouter une alimentation")
                            truc = self.safeInput()
                            if truc == '1':
                                print("\n> Liste des alimentations : \n")
                                self.displayAlimentationList()

                            elif truc == '2':
                                print("\n> Ajouter une alimentation : ")
                                fullInterfaces = self.parent.res('interfaces')
                                interfaces = []
                                for interface in fullInterfaces:
                                    if interface.allowAiguillageHandling == True:
                                        interfaces.append(interface)
                                self.displayInterfacesList(filter=True, allowAiguillageHandling=True)
                                print("> Entrez le numéro de l'interface souhaitée : ")
                                interface = interfaces[int(self.safeType('')) - 1]

                                name = self.safeType("Entrez le nom : ")
                                pin = int(self.safeType("Entrez le pin : "))
                                newAlim = Alimentation(name, pin)
                                #interface.addAlimentation(newAlim)
                                addAlimentation = lambda interface, alim: interface.addAlimentation(alim)
                                self.sync(addAlimentation, interface, newAlim)

                            continue
                        elif truc == '2':
                            print("\n++ Ajouter un aiguillage ++\n")
                            self.constructAiguillage()
                        elif truc == '4':
                            print("\n++ Manipuler les aiguillages ++")
                            print ("> Sélectionnez l'aiguillage à manipuler : ")
                            self.displayAiguillageList()
                            truc = self.safeType('id : ', number=True) - 1
                            toSwitch = self.parent.res('aiguillages')[truc]

                            direction = self.getValidDirections(toSwitch[1], input=True)
                            switch = lambda toSwitch, direction: toSwitch.switch(direction)
                            self.sync(switch, toSwitch[1], direction)

                        elif truc == 's':
                            print("> Sauvegarde...")
                            self.queue('save', None)



                print('console thread finished')

            except ProgrammStoppedExcept as ex:
                print('programm stopped for reason : ' + ex.message)
                return

        def safeType(self, message, number = False):
            valid = False
            toReturn = None
            while True:
                toReturn = input('> ' + message)
                if toReturn == 'x':
                    stop = lambda self: self.parent.stop()
                    self.sync(stop, self)
                    self.queue('stop', None)
                    raise ProgrammStoppedExcept("Le programme s'est arrêté normalement.")
                if number == True:
                    try:
                        toReturn = int(toReturn)
                    except ValueError:
                        print("> Bad entry, try again : ")
                    else:
                        valid = True
                        return toReturn

                if number != True or (number == True and valid != False):
                    break

            return toReturn

        def safeInput(self, number = False):
            isValid = False
            toReturn = ''
            while True:
                toReturn = readchar.readkey()
                if number == True and toReturn != 'x':# au cas où on voudrait quitter en cours d'input d'un nombre...
                    try:
                        toReturn = int(toReturn)
                    except ValueError:
                        print('> Bad input, try again : ')
                    else:
                        isValid = True
                        break
                else:
                    break
            if (toReturn == 'x' or toReturn == readchar.key.END):
                stop = lambda self: self.parent.stop()
                self.sync(stop, self)
                self.queue('stop', None)
                raise ProgrammStoppedExcept("Le programme c'est arrêté normalement")
            return toReturn

        def displayAiguillageList(self):
            aiguillageList = self.parent.res('aiguillages')
            print(aiguillageList)
            print("\n\nID |NOM                 |DIR")
            for aiguillages in aiguillageList:
                count = 1
                aiguillage = aiguillages[1]
                print('{:3}|{:20}|{:3}'.format(count, aiguillage.name, Direction.getAbbDir(aiguillage.currentDirection)))
                count += 1

            print('\n\n')

        def displayAlimentationList(self):
            alimentations = []
            interfaces = self.parent.res('interfaces')
            for interface in interfaces:
                if interface.allowAiguillageHandling == True and interface.compatibleSinglePinMode == True:
                    for alimentation in interface.alimentations:
                        alimentations.append(alimentation[1])
            print("\n \nID |Nom                 |PIN")
            count = 1
            for alimentation in alimentations:
                print("{:3d}|{:20s}|{:3d}".format(count, alimentation.name, alimentation.pin))
                count += 1

        def displayInterfacesList(self, filter=False, allowUserInteraction=False, allowAiguillageHandling=False):
            toDisplay = []
            interfaces = self.parent.res('interfaces')
            if filter == False:
                return interfaces
            else:
                for interface in interfaces:
                    if (interface.allowUserInteraction == True and allowUserInteraction == True) or (interface.allowAiguillageHandling == True and allowAiguillageHandling == True):
                        toDisplay.append(interface)

            print("ID |NOM                           |")
            count = 1
            for interface in toDisplay:
                print("{:3d}|{:30s}|".format(count, interface.id))
                count += 1

        def getDirection(self, input=False):
            print("> Directions : ")
            count = 1
            for direction in Direction.directionsList:
                print(str(count) + ". " + direction)
                count += 1
            if (input == True):
                return Direction.directionsList[self.safeInput(number=True) - 1]

        def getValidDirections(self, aiguillage, input=False):
            print("> Directions valides pour l'aiguillage " + aiguillage.name)
            count = 1
            for direction in aiguillage.directions:
                print(str(count) + ". " + direction.direction)
                count += 1
            if (input == True):
                return Direction.directionsList[int(self.safeInput()) - 1]

        def constructAiguillage(self):
            print("> Entrez le type de l'aiguillage : ")
            aiguillageType = self.safeType("type de l'aiguillage : ")
            builder = AiguillageBuilder.getAiguillageBuilder(aiguillageType)
            print("Taille du builder : " + str(len(builder)))

            self.displayInterfacesList(filter = True, allowAiguillageHandling= True)

            fullInterfaces = self.parent.res('interfaces')
            interfaces = []
            for interface in fullInterfaces:
                if interface.allowAiguillageHandling == True:
                    interfaces.append(interface)

            interface = interfaces[self.safeType('id de l\'interface : ', number = True) - 1]

            for item, type in builder.items():
                if type == 'string':
                    builder[item] = self.safeType("Entrez : " + item + '\n')

                elif type == 'direction':
                    print("> Entrez : " + item + "\n")
                    builder[item] = self.getDirection(input=True)

                elif type == 'alimentation':
                    fullInterfaces = self.parent.res("interfaces")
                    alimInterfaces = []
                    for linterface in fullInterfaces:
                        if linterface.allowAiguillageHandling == True and linterface.compatibleSinglePinMode == True:
                            alimInterfaces.append(linterface)
                    alimentations = []
                    for linterface in alimInterfaces:
                        for alimentation in linterface.alimentations:
                            alimentations.append(alimentation[1])

                    print("> Entrez : " + item + "\n")
                    self.displayAlimentationList()
                    truc = self.safeType('id : ', number = True) - 1
                    builder[item] = alimentations[truc]

                elif type == 'pinStateList':
                    print("> Entrez : " + item)
                    print("  (entrée pour nouvel item, del pour confirmer)\n")
                    pinStates = []
                    quit = False
                    while quit == False:
                        print("Nouvel item : Entrez direction : ")
                        direction = self.getDirection(input=True)

                        print("Entrez numéro de pin : ")
                        pinNum = self.safeType('',number = True)

                        print("Entrez état du pin : ")
                        print("1. éteint")
                        print("2. allumé")
                        valid = False
                        state = None
                        while valid == False:
                            state = self.safeInput()
                            if state == '1':
                                state = AlimentationState.LOW
                                valid = True
                            elif state == '2':
                                state = AlimentationState.HIGH
                                valid = True
                            else:
                                print("> Bad entry, try again...")

                        pinStates.append(PinState(pinNum, state, direction))
                        print("continuer ? (O/N)")
                        truc = None
                        while True:
                            truc = self.safeInput()
                            if truc == 'O' or truc == 'o':
                                quit = False
                                print("> Nouvel item : ")
                                break
                            elif truc == 'n' or truc == 'N':
                                quit = True
                                break

                    builder[item] = pinStates
            newAiguillage = AiguillageBuilder.constructAiguillage(aiguillageType, builder)
            print("Aiguillage construit ! ")
            #interface.addAiguillage(newAiguillage)
            addAiguillage = lambda interface, aiguillage : interface.addAiguillage(aiguillage)
            self.sync(addAiguillage, interface, newAiguillage)
            print("\n")

        #END ConsoleThread
    def __init__(self, res, save = None):
        super().__init__()

        self.processListLock = RLock()
        self.processList = []
        self.isStopping = False

        self.consoleThread = ConsoleUserHandler.ConsoleThread(self, self.isStopping)
        self.res = res

    def launch(self):
        self.consoleThread.start()

    def save(self):
        return super().save()
