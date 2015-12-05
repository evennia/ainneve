"""
Armor typeclasses
"""

from typeclasses.items import Equippable

class Armor(Equippable):
    """
    Typeclass for armor objects.

    Attributes:
        toughness (int): primary defensive stat
    """
    toughness = 0
    slots = ['armor']

    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.toughness = self.toughness

    def at_equip(self, character):
        character.traits.DEF.mod += self.db.toughness

    def at_remove(self, character):
        character.traits.DEF.mod -= self.db.toughness


class Shield(Armor):
    """Typeclass for shield prototypes."""
    slots = ['wield1', 'wield2']
    multi_slot = False

