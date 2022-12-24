"""
Test Ainneve's custom commands.

"""

from unittest.mock import call, patch

from anything import Something

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest

from commands import combat
from typeclasses.characters import Character
from typeclasses.npcs import Mob, ShopKeeper

from world.combat import CombatHandler
from world.enums import CombatRange

from .mixins import AinneveTestMixin


class TestCombatHandler(AinneveTestMixin, EvenniaTest):
    def setUp(self):
        super().setUp()
        self.combat = CombatHandler(self.char1, self.char2)
        self.combat.positions[self.char1] = 1
        self.combat.positions[self.char2] = 2

    def test_add_remove(self):
        target = create_object(Mob, key="rat", location=self.room1)
        self.combat.add(target)
        self.assertTrue(target in self.combat.positions)
        self.combat.remove(target)
        self.assertFalse(target in self.combat.positions)

    def test_approach(self):
        self.combat.approach(self.char1, self.char2)
        self.assertEqual(
            self.combat.positions[self.char1], self.combat.positions[self.char2]
        )
        self.assertFalse(self.combat.approach(self.char1, self.char2))

    def test_retreat(self):
        # retreating negative
        self.combat.retreat(self.char1, self.char2)
        self.assertEqual(self.combat.positions[self.char1], 0)
        self.assertEqual(self.combat.positions[self.char2], 2)
        # retreating positive
        self.combat.retreat(self.char2, self.char1)
        self.assertEqual(self.combat.positions[self.char1], 0)
        self.assertEqual(self.combat.positions[self.char2], 3)

    def test_in_range(self):
        self.assertTrue(self.combat.in_range(self.char1, self.char2, "MELEE"))
        self.combat.positions[self.char2] = 5
        self.assertFalse(self.combat.in_range(self.char1, self.char2, "MELEE"))
        self.assertTrue(self.combat.in_range(self.char1, self.char2, "RANGED"))

    def test_any_in_range(self):
        self.assertTrue(self.combat.any_in_range(self.char1, "MELEE"))
        self.combat.positions[self.char2] = 5
        self.assertFalse(self.combat.any_in_range(self.char1, "MELEE"))
        self.assertTrue(self.combat.any_in_range(self.char1, "RANGED"))

    def test_get_range(self):
        self.assertEqual(self.combat.get_range(self.char1, self.char2), "MELEE")
        self.combat.positions[self.char2] = 5
        self.assertEqual(self.combat.get_range(self.char1, self.char2), "RANGED")


class TestCombatCommands(AinneveTestMixin, EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.target = create_object(Mob, key="rat", location=self.room1)

    def tearDown(self):
        super().tearDown()
        self.target.delete()

    def test_engage(self):
        self.call(
            combat.CmdInitiateCombat(),
            "rat",
            "You prepare for combat! rat is at melee range.",
        )
        self.assertEqual(self.char1.ndb.combat, self.target.ndb.combat)

        self.call(
            combat.CmdInitiateCombat(),
            "char2",
            "You can't attack another player here.",
        )
        self.call(
            combat.CmdInitiateCombat(),
            "obj",
            "You can't attack that.",
        )

    def test_hit(self):
        combat_instance = CombatHandler(self.char1, self.target)
        self.call(
            combat.CmdHit(),
            "rat",
            "You hit rat with your Empty Fists",
        )
        self.char1.cooldowns.clear()
        combat_instance.retreat(self.char1, self.target)
        self.call(
            combat.CmdHit(),
            "rat",
            "rat is too far away.",
        )

    def test_shoot(self):
        combat_instance = CombatHandler(self.char1, self.target)
        self.weapon.attack_range = CombatRange.RANGED
        self.weapon.location = self.char1
        self.char1.equipment.move(self.weapon)
        self.call(
            combat.CmdShoot(),
            "rat",
            "You shoot rat with your weapon",
        )
        self.char1.cooldowns.clear()
        combat_instance.retreat(self.char1, self.target)
        self.call(
            combat.CmdShoot(),
            "rat",
            "You shoot rat with your weapon",
        )

    def test_flee(self):
        combat_instance = CombatHandler(self.char1, self.target)
        self.call(
            combat.CmdFlee(),
            "",
            "You flee!",
        )
        self.assertFalse(self.char1.nattributes.has("combat"))
        self.assertFalse(self.target.nattributes.has("combat"))
        self.assertEqual(self.char1.location, self.room2)
