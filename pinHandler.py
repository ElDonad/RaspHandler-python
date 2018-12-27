# -*- coding: utf-8 -*-

class gpio:

    BOARD = 0
    BCM = 1
    OUT = 'out'
    IN = 'in'
    LOW = 'low'
    HIGH = 'high'
    def init():
        print('[GPIO]Init gpio...')

    def setMode():
        print('[GPIO]setting GPIO mode to BCM')

    def setup(pin, mode= OUT):
        print('[GPIO]setting ' + str(pin) + 'to ' + mode)

    def output(pin, state):
        print('[GPIO]setting pin ' + str(pin) + ' at state : ' + state)
