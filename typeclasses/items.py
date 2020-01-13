"""
Generic Item typeclasses
"""

from typeclasses.objects import Object
from evennia import create_object
from evennia.prototypes.spawner import spawn


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
                                 "get:true()"
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


class Bundlable(Item):
    """Typeclass for items that can be bundled."""
    def at_object_creation(self):
        super(Bundlable, self).at_object_creation()
        self.db.bundle_size = 999
        self.db.prototype_name = None

    def at_get(self, getter):
        super(Bundlable, self).at_get(getter)
        bundle_key = self.aliases.all()[0]
        others = [obj for obj in getter.contents
                  if obj.is_typeclass('typeclasses.items.Bundlable')
                  and bundle_key in obj.aliases.all()]

        if len(others) >= self.db.bundle_size \
                and self.db.prototype_name and self.aliases.all():

            # we have enough to create a bundle

            bundle = create_object(
                typeclass='typeclasses.items.Bundle',
                key='a bundle of {}s'.format(bundle_key),
                aliases=['bundle {}'.format(bundle_key)],
                location=self.location
            )
            bundle.db.desc = ("A bundle of {item}s held together "
                              "with a thin leather strap.").format(
                item=bundle_key
            )
            bundle.db.value = self.db.bundle_size * self.db.value
            bundle.db.weight = self.db.bundle_size * self.db.weight
            bundle.db.quantity = self.db.bundle_size
            bundle.db.prototype_name = self.db.prototype_name
            for obj in others[:self.db.bundle_size]:
                obj.delete()


class Bundle(Item):
    """Typeclass for bundles of Items."""
    def expand(self):
        """Expands a bundle into its component items."""
        for i in list(range(self.db.quantity)):
            p = self.db.prototype_name
            spawn(dict(prototype=p, location=self.location))
        self.delete()


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
