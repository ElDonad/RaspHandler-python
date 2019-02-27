from interface import Interface
from aiguillage import AlimentationState
from EventObj import EventObj
from AiguillageBuilder import AiguillageBuilder


class Alimentation(EventObj):
    compatibleSinglePinMode = False

    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        self.state = AlimentationState.LOW
        self.requestedOpen = 0   # Permet de savoir combien d'aiguillages ont besoin de l'alimentation.

    def __eq__(a, b):
        if a.name == b.name and a.pin == b.pin:
            return True
        return False

    def serialize(self):
        return {
            'name': self.name,
            'pin': self.pin,
            'pin_state': self.state
        }


class AiguillageHandler(Interface):

    def __init__(self):
        super().__init__()
        self.aiguillages = []

    def addAiguillage(self, aiguillage):
        newAiguillage = {}
        newAiguillage['aiguillage'] = aiguillage
        newAiguillage['switchedId'] = aiguillage.subscribe('switched', self.aiguillageSwitched)
        self.aiguillages.append(newAiguillage)

    def deleteAiguillage(self, aiguillage):
        for tocheck in self.aiguillages:
            if tocheck['aiguillage'] == aiguillage:
                self.emit('aiguillageDeleted', aiguillage)
                del tocheck

    def aiguillageSwitched(self, aiguillage, args):
        self.emit('aiguillageSwitched', {'aiguillage': aiguillage, 'args': args})

    def save(self):
        toReturn = super().save()

        saveAiguillage = []
        for aiguillage in self.aiguillages:
            saveAiguillage.append(aiguillage.save())
        toReturn.update({
            'aiguillages': saveAiguillage,
            'compatibleSinglePinMode': self.compatibleSinglePinMode
        })
        return toReturn

    def restore(self, data):
        super().restore(data)
        restoreAiguillages = []
        for aigData in data['aiguillages']:
            newAiguillage = AiguillageBuilder.constructAiguillage(aigData['type'], {'postInit': True})
            newAiguillage.restore(aigData)
            restoreAiguillages.append(newAiguillage)

        self.aiguillages = restoreAiguillages
        self.compatibleSinglePinMode = data['compatibleSinglePinMode']
