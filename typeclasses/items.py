"""
Generic Item typeclasses
"""

from typeclasses.objects import Object


class Item(Object):
    """
    Typeclass for Items.
    """

    # monetary value of the item in CC
    value = 0
    # weight of the item
    weight = 0

    def at_object_creation(self):
        super(Item, self).at_object_creation()
        self.locks.add("puppet:perm(Wizards)")
        self.db.value = self.value
        self.db.weight = self.weight

class Equippable(Object):
    """
    Mixin typeclass for equippable Items.
    """

    # list of slots for equipping
    slots = None
    # operator to use when specifying multiple slots
    slot_operator = 'AND'

    def at_object_creation(self):
        super(Equippable, self).at_object_creation()
        self.db.slot = self.slots
        self.db.slot_operator = self.slot_operator
        self.locks.add("puppet:false();equip:true()")

