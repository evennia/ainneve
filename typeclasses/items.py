"""
Generic Item typeclasses
"""

from typeclasses.objects import Object

class Item(Object):
    def at_object_creation(self):
        super(Item, self).at_object_creation()
        self.value = 0
        self.weight = 0
