"""
Weapon typeclasses
"""

from typeclasses.items import Equippable


class Weapon(Equippable):
    """
    Typeclass for weapon objects.

    Attributes:
        damage (int): primary attack stat
        handedness (int): indicates single- or double-handed weapon
    """
    slots = ['wield1', 'wield2']
    multi_slot = False

    damage = 0
    handedness = 1

    def at_object_creation(self):
        super(Weapon, self).at_object_creation()
        self.db.damage = self.damage
        self.db.handedness = self.handedness

    def at_equip(self, character):
        character.traits.ATKM.mod += self.db.damage

    def at_remove(self, character):
        character.traits.ATKM.mod -= self.db.damage

class RangedWeapon(Weapon):
    """
    Typeclass for thrown and single-handed ranged weapon objects.

    Attributes:
        range (int): range of weapon in (units?)
        ammunition Optional(str): type of ammunition used (thrown if None)
    """
    range = 0
    ammunition = None

    def at_object_creation(self):
        super(RangedWeapon, self).at_object_creation()
        self.db.range = self.range
        self.db.ammunition = self.ammunition

    def at_equip(self, character):
        character.traits.ATKR.mod += self.db.damage

    def at_remove(self, character):
        character.traits.ATKR.mod -= self.db.damage


class TwoHanded(object):
    """Mixin class for two handed weapons."""
    slots = ['wield1', 'wield2']
    multi_slot = True
    handedness = 2


class TwoHandedWeapon(Weapon, TwoHanded):
    """Typeclass for two-handed melee weapons."""
    pass


class TwoHandedRanged(TwoHanded, RangedWeapon):
    """Typeclass for two-handed ranged weapons."""
    pass


