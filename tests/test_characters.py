"""
Test characters.

"""

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest


class TestCharacters(EvenniaTest):
    def test_abilities(self):
        self.char1.strength += 2
        self.assertEqual(self.char1.strength, 3)

    def test_heal(self):
        """Make sure we don't heal too much"""
        self.char1.hp = 0
        self.char1.hp_max = 8

        self.char1.heal(1)
        self.assertEqual(self.char1.hp, 1)
        self.char1.heal(100)
        self.assertEqual(self.char1.hp, 8)

    def test_at_damage(self):
        self.char1.hp = 8
        self.char1.at_damage(5)
        self.assertEqual(self.char1.hp, 3)

    def test_at_pay(self):
        self.char1.coins = 100

        result = self.char1.at_pay(60)
        self.assertEqual(result, 60)
        self.assertEqual(self.char1.coins, 40)

        # can't get more coins than we have
        result = self.char1.at_pay(100)
        self.assertEqual(result, 40)
        self.assertEqual(self.char1.coins, 0)
