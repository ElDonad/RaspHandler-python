# -*- coding: utf-8 -*-

from AiguillageHandler import AiguillageHandler
from aiguillage import Aiguillage, AlimentationState
from pinHandler import gpio

class DirectAiguillageHandler(AiguillageHandler):

    compatibleSinglePinMode = True
    allowUserInteraction = False
    allowAiguillageHandling = True
    id='DirectAiguillageHandler'

    def __init__(self, res, data = None):
        super().__init__()
        self.claimedPinStates = []
        self.alimentations = []
        self.res = res
        if data != None:
            self.restore(data)

    def addAiguillage(self, aiguillage):
        for direction in aiguillage.directions:
            if direction in self.claimedPinStates:
                return (False, 'PinStatePreviouslyClaimedError', 'Pin State already taken by other device.')
            else:
                #self.claimedPinStates.append(aiguillage) Pas comme ça ! TODO le refaire proprement
                aiguillage.subscribe('toggleAlimentation', self, DirectAiguillageHandler.toggleAlimentation)
                aiguillage.subscribe('setPinState', self, DirectAiguillageHandler.setPinState)
                aiguillage.subscribe('setupPin', self, DirectAiguillageHandler.setupPin)
                aiguillage.subscribe('aiguillageSwitched', self, DirectAiguillageHandler.aiguillageSwitched)

                aiguillage.init()
                self.aiguillages.append(aiguillage)
                self.emit('AiguillageAdded', aiguillage)
                return (True)

    def addAlimentation(self, alimentation):
        self.alimentations.append((0,alimentation))
        gpio.setup(alimentation.pin, gpio.OUT)
        self.emit('alimentationAdded', alimentation)

    def toggleAlimentation(self, args):
        for alimentation in self.alimentations:
            if args['alimentation'] == alimentation[1]:
                if args['state'] == AlimentationState.HIGH:
                    alimentation = (alimentation[0] + 1, alimentation[1])
                elif args['state'] == AlimentationState.LOW:
                    alimentation = (alimentation[0] - 1, alimentation[1])
                if alimentation[0] > 0:
                    gpio.output(alimentation[1].pin, gpio.HIGH)
                else:
                    gpio.output(alimentation[1].pin, gpio.LOW)

    def setPinState(self, pinState):
        gpio.output(pinState.pin, AlimentationState.toGpioState(pinState.pinState))

    def setupPin(self, args):
        gpio.setup(args['pin'], gpio.OUT)

    def aiguillageSwitched(self, args):
        print("[DIRECTAIGUILLAGEHANDLER]aiguillage switched")
        self.emit('aiguillageSwitched', args)#args : aiguillage

    def save(self):
        print(super().save())
        toReturn = super().save()
        toReturn.update({
            'claimedPinStates' : self.claimedPinStates,
            'alimentations' : self.alimentations

        })
        return toReturn

    def restore(self, data):
        super().restore(data)
        self.claimedPinStates = data['claimedPinStates']
        self.alimentations = data['alimentations']
        for aiguillage in self.aiguillages:
            aiguillage.subscribe('toggleAlimentation', self, DirectAiguillageHandler.toggleAlimentation)
            aiguillage.subscribe('setPinState', self, DirectAiguillageHandler.setPinState)
            aiguillage.subscribe('setupPin', self, DirectAiguillageHandler.setupPin)
            aiguillage.subscribe('aiguillageSwitched', self, DirectAiguillageHandler.aiguillageSwitched)

            aiguillage.init()

    def update(self):
        pass
