# A trivial test for Travis

from evennia.commands.default.tests import CommandTest
from commands.equip_commands import CmdEquip
from typeclasses.characters import Character

class TestEquip(CommandTest):
    character_typeclass = Character
    def test_equip(self):
        self.call(CmdEquip(), "", "You have nothing in your equipment.")
