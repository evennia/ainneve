"""
Armor typeclasses
"""

from typeclasses.items import Equippable
from commands.item_commands import EmpoweredArmorCmdSet

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


class EmpoweredArmor(Armor):
    """Armor that allows the user to boost their Defense stat."""
    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.ability_cost = [(0, 'activate')]
        self.cmdset.add(EmpoweredArmorCmdSet())
