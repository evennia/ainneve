"""
Armor typeclasses
"""

from typeclasses.items import Item

class Armor(Item):
    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.toughness = 0
        self.abilities = []
        self.slots = []
