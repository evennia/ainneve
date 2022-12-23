"""
Test Ainneve's custom commands.

"""

from unittest.mock import call, patch

from anything import Something

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from commands import game
from typeclasses.characters import Character
from typeclasses.npcs import Mob, ShopKeeper
from .mixins import AinneveTestMixin


class TestCommands(AinneveTestMixin, EvenniaCommandTest):
    def test_inventory(self):
        self.call(
            game.CmdInventory(),
            "inventory",
            """
You are fighting with your bare fists and have no shield.
You wear no armor and no helmet.
Backpack is empty.
You use 0/11 equipment slots.
""".strip(),
        )

    # @patch("commands.game.join_combat")
    # def test_attack(self, mock_join_combat):
        # self.room1.allow_combat = True

        # target = create_object(Mob, key="Ogre", location=self.room1)

        # self.call(game.CmdAttackTurnBased(), "ogre", "")

        # mock_join_combat.assert_called_with(self.char1, target, session=Something)

        # target.delete()

    def test_wield_or_wear(self):
        self.char1.equipment.add(self.helmet)
        self.char1.equipment.add(self.weapon)
        self.shield.location = self.room1

        self.call(game.CmdWieldOrWear(), "shield", "Could not find 'shield'")
        self.call(game.CmdWieldOrWear(), "helmet", "You put helmet on your head.")
        self.call(
            game.CmdWieldOrWear(),
            "weapon",
            "You hold weapon in your strongest hand, ready for action.",
        )
        self.call(game.CmdWieldOrWear(), "helmet", "You are already using helmet.")

    def test_remove(self):
        self.char1.equipment.add(self.helmet)
        self.call(game.CmdWieldOrWear(), "helmet", "You put helmet on your head.")

        self.call(game.CmdRemove(), "helmet", "You stash helmet in your backpack.")

    def test_give__coins(self):
        self.char2.key = "Friend"
        self.char2.coins = 0
        self.char1.coins = 100

        self.call(game.CmdGive(), "40 coins to friend", "You give Friend 40 coins.")
        self.assertEqual(self.char1.coins, 60)
        self.assertEqual(self.char2.coins, 40)

        self.call(game.CmdGive(), "10 to friend", "You give Friend 10 coins.")
        self.assertEqual(self.char1.coins, 50)
        self.assertEqual(self.char2.coins, 50)

        self.call(game.CmdGive(), "60 to friend", "You only have 50 coins to give.")

    @patch("commands.game.EvMenu")
    def test_give__item(self, mock_EvMenu):
        self.char2.key = "Friend"
        self.char1.equipment.add(self.helmet)

        self.call(game.CmdGive(), "helmet to friend", "")

        mock_EvMenu.assert_has_calls(
            (
                call(
                    self.char2,
                    {"node_receive": Something, "node_end": Something},
                    item=self.helmet,
                    giver=self.char1,
                ),
                call(
                    self.char1,
                    {"node_give": Something, "node_end": Something},
                    item=self.helmet,
                    receiver=self.char2,
                ),
            )
        )

    @patch("typeclasses.npcs.EvMenu")
    def test_talk(self, mock_EvMenu):
        npc = create_object(ShopKeeper, key="shopkeep", location=self.room1)

        npc.menudata = {"foo": None, "bar": None}

        self.call(game.CmdTalk(), "shopkeep", "")

        mock_EvMenu.assert_called_with(
            self.char1,
            {"foo": None, "bar": None},
            startnode="node_start",
            session=None,
            npc=npc,
        )
