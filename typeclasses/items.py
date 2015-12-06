"""
Generic Item typeclasses
"""

from typeclasses.objects import Object


class Item(Object):
    """
    Typeclass for Items.

    Attributes:
        value (int): monetary value of the item in CC
        weight (float): weight of the item
    """
    value = 0
    weight = 0.0

    def at_object_creation(self):
        super(Item, self).at_object_creation()
        self.locks.add(";".join(("puppet:perm(Wizards)",
                                 "equip:false()",
                                 "hold:true()"
                                 )))
        self.db.value = self.value
        self.db.weight = float(self.weight)

    def at_get(self, getter):
        getter.traits.ENC.current += self.db.weight
        getter.traits.MV.mod = \
            int(-(getter.traits.ENC.actual // (2 * getter.traits.STR.actual)))

    def at_drop(self, dropper):
        dropper.traits.ENC.current -= self.db.weight
        dropper.traits.MV.mod = \
            int(-(dropper.traits.ENC.actual // (2 * dropper.traits.STR.actual)))


class Equippable(Item):
    """
    Typeclass for equippable Items.

    Attributes:
        slots (str, list[str]): list of slots for equipping
        multi_slot (bool): operator for multiple slots. False equips to
            first available slot; True requires all listed slots available.
    """
    slots = None
    multi_slot = False

    def at_object_creation(self):
        super(Equippable, self).at_object_creation()
        self.locks.add("puppet:false();equip:true()")
        self.db.slots = self.slots
        self.db.multi_slot = self.multi_slot
        self.db.used_by = None

    def at_equip(self, character):
        """
        Hook called when an object is equipped by character.

        Args:
            character: the character equipping this object
        """
        pass

    def at_remove(self, character):
        """
        Hook called when an object is removed from character equip.

        Args:
            character: the character removing this object
        """
        pass

    def at_drop(self, dropper):
        super(Equippable, self).at_drop(dropper)
        if self in dropper.equip:
            dropper.equip.remove(self)
            self.at_remove(dropper)
