"""
Weapon typeclasses
"""

from typeclasses.items import Item

class Weapon(Item):
    def at_object_creation(self):
        super(Weapon, self).at_object_creation()
        self.damage = 0
        self.handedness = 1
        self.abilities = []

class RangedWeapon(Weapon):
    def at_object_creation(self):
        super(RangedWeapon, self).at_object_creation()
        self.range = 0
