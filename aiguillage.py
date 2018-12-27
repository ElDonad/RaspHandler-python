from EventObj import EventObj
from pinHandler import gpio

class Direction:
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'
    INVALID = 'invalid'
    def getAbbDir(direction):
        if direction == Direction.LEFT:
            return 'LFT'
        elif direction == Direction.RIGHT:
            return 'RGT'
        elif direction == Direction.MIDDLE:
            return 'MID'
        elif direction == Direction.INVALID:
            return 'INV'

    directionsList = [
        LEFT,
        RIGHT,
        MIDDLE
    ]

class AlimentationState:
    HIGH = 1
    LOW = 0
    UNDEFINED = -1
    def toGpioState(state):
        if state == AlimentationState.HIGH:
            return gpio.HIGH
        else:
            return gpio.LOW

class PinState:
    def __init__(self, pin, state, direction):
        self.direction = direction
        self.pin = pin
        self.pinState = state

    def __eq__(self, other):
        if self.direction == other.direction and self.pin == other.pin and self.pinState == other.pinState:
            return True
        return False

class Aiguillage(EventObj):

    compatibleSinglePinMode = False
    composer = {'name':'string', 'defaultDirection':'direction'}
    type = 'Aiguillage'

    def __init__(self, name, directions):
        self.name = name
        self.directions = directions #tuple: ( int, direction: string, pinState : dict)

    targetDirection = 0
    currentDirection = 0
    def save(self):
        return {
            'name':self.name,
            'targetDirection':self.targetDirection,
            'currentDirection':self.currentDirection,
            'directions':self.directions,
            'type':self.type
        }

    def restore(self, data):
        self.name = data['name']
        self.targetDirection = data['targetDirection']
        self.currentDirection = data['currentDirection']
        self.directions = data['directions']
