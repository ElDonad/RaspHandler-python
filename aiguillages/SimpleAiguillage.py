# -*- coding: utf-8 -*-

from aiguillage import Aiguillage, AlimentationState, Direction
from threading import Thread
from time import sleep


class SimpleAiguillage(Aiguillage):

    schema = {
        'name': {'type': 'string'},
        'alimentation': {'type': 'alimentation'},
        'defaultDirection': {'type': 'direction', 'values': ["Left", "Right", "Middle"]},
        'directions': {'type': 'pinStateList'}
    }
    type = 'SimpleAiguillage'

    def __init__(self, directions=None, defaultDirection=None, alimentation=None, name=None, fromBuilder=False, builderData={}, postInit=False):
        super().__init__()
        if postInit is True:
            return

        if fromBuilder is False:
            self.name = name
            self.directions = directions  # type : [pinState,...]
            self.targetDirection = defaultDirection
            self.currentDirection = Direction.INVALID
            self.alimentation = alimentation
        else:
            if 'postInit' in builderData and builderData['postInit'] is True:
                return
            self.directions = builderData['directions']
            self.targetDirection = builderData['defaultDirection']
            self.currentDirection = Direction.INVALID
            self.alimentation = builderData['alimentation']
            self.name = builderData['name']

    def init(self):
        currentPinState = None
        for direction in self.directions:
            if direction.direction == self.targetDirection:
                currentPinState = direction
        self.emit('setupPin', {
            'pin': currentPinState.pin})
        self.switchThread = SimpleAiguillage.SimpleAiguillageSwitcher(self)
        self.switchThread.start()

    def switch(self, targetDirection):
        print("Coucou, du switch" + targetDirection)
        self.targetDirection = targetDirection
        self.switchThread = SimpleAiguillage.SimpleAiguillageSwitcher(self)
        self.switchThread.start()
        self.emit('aiguillageSwitched', {
            'aiguillage': self,
            'direction': targetDirection
        })

    def save(self):
        toReturn = super().save()
        toReturn.update({
            'alimentation': self.alimentation
        })
        return toReturn

    def restore(self, data):
        super().restore(data)
        self.alimentation = data['alimentation']

    def serialize(self):
        toReturn = super().serialize()
        toReturn.update({
            'alimentation': self.alimentation.serialize()
        })
        return toReturn

    class SimpleAiguillageSwitcher(Thread):
        def __init__(self, aiguillage):
            Thread.__init__(self)
            self.aiguillage = aiguillage

        def run(self, emergency=False):
            timer = 0
            if emergency is False:
                timer = 0.15
            else:
                timer = 1
            self.aiguillage.emit('toggleAlimentation', {
                'alimentation': self.aiguillage.alimentation,
                'state': AlimentationState.HIGH
            })
            targetPinState = None
            for pinState in self.aiguillage.directions:
                if pinState.direction == self.aiguillage.targetDirection:
                    targetPinState = pinState
            self.aiguillage.emit('setPinState', targetPinState)

            sleep(timer)
            self.aiguillage.emit('toggleAlimentation', {
                'alimentation': self.aiguillage.alimentation,
                'state': AlimentationState.LOW
            })
            print('aiguillage switched')
            self.aiguillage.currentDirection = self.aiguillage.targetDirection
