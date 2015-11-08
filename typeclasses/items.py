"""
Generic Item typeclasses
"""

from typeclasses.objects import Object


class Item(Object):
    """Typeclass for Items.

    Attributes:
      value (int): monetary value of the item in CC
      weight (int): weight of the item
    """
    value = 0
    weight = 0

    def at_object_creation(self):
        super(Item, self).at_object_creation()
        self.locks.add(";".join(("puppet:perm(Wizards)",
                                 "equip:false()",
                                 "hold:true()"
                                 )))
        self.db.value = self.value
        self.db.weight = self.weight


class Equippable(Item):
    """Typeclass for equippable Items.

    Attributes:
      slots (str, list[str]): list of slots for equipping
      multi_slot (bool): operator for multiple slots. False equips to
          first available slot; True requires all listed slots available.
    """
    slots = None
    slot_operator = False

    def at_object_creation(self):
        super(Equippable, self).at_object_creation()
        self.locks.add("puppet:false();equip:true()")
        self.db.slot = self.slots
        self.db.slot_operator = self.slot_operator

    def at_equip(self, character):
        """Hook called when an object is equipped by character.

        Args:
          character: the character equipping this object
        """
        pass

    def at_remove(self, character):
        """Hook called when an object is removed from character equip.

        Args:
          character: the character removing this object
        """
        pass


