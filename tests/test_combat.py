"""
Test Ainneve's custom commands.

"""

from commands import combat
from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
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
        from typeclasses.mobs.mob import BaseMob
        target = create_object(BaseMob, key="rat", location=self.room1)
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
        self.assertTrue(self.combat.in_range(self.char1, self.char2, CombatRange.MELEE))
        self.combat.positions[self.char2] = 5
        self.assertFalse(self.combat.in_range(self.char1, self.char2, CombatRange.MELEE))
        self.assertTrue(self.combat.in_range(self.char1, self.char2, CombatRange.RANGED))

    def test_any_in_range(self):
        self.assertTrue(self.combat.any_in_range(self.char1, CombatRange.MELEE))
        self.combat.positions[self.char2] = 5
        self.assertFalse(self.combat.any_in_range(self.char1, CombatRange.MELEE))
        self.assertTrue(self.combat.any_in_range(self.char1, CombatRange.RANGED))

    def test_get_range(self):
        self.assertEqual(self.combat.get_range(self.char1, self.char2), CombatRange.MELEE)
        self.combat.positions[self.char2] = 5
        self.assertEqual(self.combat.get_range(self.char1, self.char2), CombatRange.MEDIUM)


class TestCombatCommands(AinneveTestMixin, EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        from typeclasses.mobs.mob import BaseMob
        self.target = create_object(BaseMob, key="rat", location=self.room1)

    def tearDown(self):
        super().tearDown()
        if self.target.dbid:
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
        combat_instance.positions[self.target] = CombatRange.RANGED
        self.call(
            combat.CmdHit(),
            "rat",
            "rat is too far away.",
        )
        combat_instance.positions[self.target] = CombatRange.MELEE
        self.call(
            combat.CmdHit(),
            "rat",
            # TODO Patch a guaranteed hit
            #"You hit rat with your fists",
        )
        self.char1.cooldowns.clear()

    def test_shoot(self):
        combat_instance = CombatHandler(self.char1, self.target)
        self.weapon.attack_range = CombatRange.RANGED
        self.weapon.location = self.char1
        self.char1.equipment.move(self.weapon)
        self.call(
            combat.CmdShoot(),
            "rat",
            # TODO Patch a guaranteed hit
            #"You shoot rat with your weapon",
        )
        self.char1.cooldowns.clear()

    def test_flee(self):
        combat_instance = CombatHandler(self.char1, self.target)
        self.call(
            combat.CmdFlee(),
            "",
            "You flee!",
        )
        self.assertFalse(self.char1.combat)
        self.assertFalse(self.target.combat)
        self.assertEqual(self.char1.location, self.room2)
