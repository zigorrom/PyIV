from enum import Enum

class PumpingMode(Enum):
    PERMANENT_PUMPING = 0
    VOLUME = 1

class PumpingDirection(Enum):
    FORWART = 0
    BACKWARD = 1

class Pump:
    def __init__(self, name, address):
        self._name = name
        self._address = address
        self._mode = None
        self._direction = None
        self._volume = None

    def initialize(self):
        raise NotImplementedError()

    def start_pumping(self):
        raise NotImplementedError()

    def stop_pumping(self):
        raise NotImplementedError()

    def calibrate(self):
        raise NotImplementedError()

    @property
    def flow_rate(self):
        raise NotImplementedError()

    @flow_rate.setter
    def flow_rate(self, value):
        raise NotImplementedError()

    @property
    def mode(self):
        raise NotImplementedError()

    @mode.setter
    def mode(self, value):
        raise NotImplementedError()

    @property
    def direction(self):
        raise NotImplementedError()
    
    @direction.setter
    def direction(self, value):
        raise NotImplementedError()

    @property
    def volume(self):
        raise NotImplementedError()

    @volume.setter
    def volume(self):
        raise NotImplementedError()

    



    


    


    

    

    
