# coding=UTF-8
#
#   File        :   statusBits.py
#
#   Author      :   GeeHB
#
#   Description : Utilisation de bits d'états
#

STATUS_NONE = 0

# Bitwise operator wrapper
#
class statusBits:
    def __init__(self, value: int = STATUS_NONE):
        self.value_: int = value

    # Access
    #
    @property
    def value(self)->int:
        return self.value_

    @value.setter
    def value(self, val : int):
        self.assign(val)

    def assign(self, value: int):
        self.value_ = value

    def set(self, bit:int , set: bool = True):
        inPlace: bool = self.isSet(bit)
        if set:
            if not inPlace:
                # on le met
                self.value_ = self.value_ | bit
        else:
            if inPlace:
                # on le retire
                self.value_ = self.value_ & ~ bit

    # Unset/remove a bit
    def remove(self, bitVal: int):
        self.set(bitVal, False)

    # Is a bit set ?
    def isSet(self, bitVal:int) -> bool:
        return False if bitVal == 0 else ((self.value_& bitVal) == bitVal)

# EOF
