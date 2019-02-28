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

    def dirToStandard(direction):
        if direction == Direction.LEFT:
            return 1
        elif direction == Direction.RIGHT:
            return 2
        elif direction == Direction.MIDDLE:
            return 3
        elif direction == Direction.INVALID:
            return 0

    def stringToDirection(direction):
        print('direction to convert : ' + direction)
        direction = direction.lower().lstrip()
        print("direction converted : " + direction)
        if direction == 'right':
            return Direction.RIGHT
        elif direction == 'left':
            return Direction.LEFT
        elif direction == 'middle':
            return Direction.MIDDLE

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

    def fromBoolToState(state):
        if state is True:
            return AlimentationState.HIGH
        else:
            return AlimentationState.LOW


class PinState:
    def __init__(self, pin, state, direction):
        self.direction = direction
        self.pin = pin
        self.pinState = state

    def __eq__(self, other):
        if self.direction == other.direction and self.pin == other.pin and self.pinState == other.pinState:
            return True
        return False

    def serialize(self):
        return {
            'direction': self.direction,
            'pin': self.pin,
            'pin_state': self.pinState
        }

    def deserialize(serializedData):
        print("deserializing...")
        print("state's direction : ", serializedData['direction'])
        truc = PinState(serializedData['pin'], serializedData['pin_state'], serializedData['direction'])
        print(truc)
        return truc


class Aiguillage(EventObj):

    compatibleSinglePinMode = False
    composer = {'name': 'string', 'defaultDirection': 'direction'}
    type = 'Aiguillage'
    nextId = 0

    def __init__(self, name=None, directions=None):
        super().__init__()
        self.name = name
        self.directions = directions  # tuple: ( int, direction: string, pinState : dict)
        self.id = Aiguillage.getNextId()

    targetDirection = 0
    currentDirection = 0

    def save(self):
        return {
            'tag': self.name,
            'target_direction': self.targetDirection,
            'current_direction': self.currentDirection,
            'directions': self.directions,
            'type': self.type,
            'id': self.id
        }

    def serialize(self):
        directionsArray = []
        for direction in self.directions:
            directionsArray.append(direction.serialize())

        return{
            'tag': self.name,
            'target_direction': self.targetDirection,
            'current_direction': self.currentDirection,
            'type': self.type,
            'directions': directionsArray,
            'aiguillage_id': self.id

        }

    def restore(self, data):
        self.name = data['tag']
        self.targetDirection = data['target_direction']
        self.currentDirection = data['current_direction']
        self.directions = data['directions']
        self.id = data['id']

    def getNextId():
        Aiguillage.nextId += 1
        return Aiguillage.nextId - 1
