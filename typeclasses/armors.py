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
        super(Armor, self).at_equip(character)
        # TODO: once traits are finalized, something like
        # character.db.traits.defense.mod += self.db.toughness
        pass

    def at_remove(self, character):
        super(Armor, self).at_remove(character)
        # TODO: once traits are finalized, something like
        # character.db.traits.defense.mod -= self.db.toughness
        pass


class Shield(Armor):
    """Typeclass for shield prototypes."""
    slots = ['wield1', 'wield2']
    multi_slot = False

