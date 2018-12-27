from EventObj import EventObj
from aiguillages.SimpleAiguillage import SimpleAiguillage

class AiguillageBuilder(EventObj):
    aiguillagesRegister = [
        {
            'name':'SimpleAiguillage',
            'params': SimpleAiguillage.schema,
            'constructor': SimpleAiguillage
        }
    ]

    @staticmethod
    def constructAiguillage(type, args):
        for aiguillage in AiguillageBuilder.aiguillagesRegister:
            if aiguillage['name'] == type:
                return aiguillage['constructor'](fromBuilder=True, builderData=args)

    @staticmethod
    def getAiguillageBuilder(type):
        for builder in AiguillageBuilder.aiguillagesRegister:
            if builder['name'] == type:
                return builder['params']
