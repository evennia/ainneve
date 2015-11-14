"""
Unit tests for world.archetypes module.
"""

from django.test import TestCase
from world import rulebook


class DiceExpressionTestCase(TestCase):
    """Test case for dice expression functions."""
    def test_parse_roll(self):
        """test parsing of XdY+Z style dice expressions"""
        rolls = {'2d6': (2, 6, 0, 0),
                 '4d4-3': (4, 4, -3, 0),
                 '4d6+4': (4, 6, 4, 0),
                 '4d10-L': (4, 10, 0, 1),
                 '5d6-2L': (5, 6, 0, 2),
                 '4d8+2-L': (4, 8, 2, 1),
                 '4d8-2-L': (4, 8, -2, 1),
                 '10d4+2-2L': (10, 4, 2, 2),
                 '10d4-2-2L': (10, 4, -2, 2),
                 }
        for roll in rolls:
            self.assertEqual(rulebook._parse_roll(roll), rolls[roll])

    def test_roll_max(self):
        """test calculation of max possible roll"""
        rolls = {'2d6': 12, '4d4-3': 13, '4d6+4': 28, '4d10-L': 30,
                 '5d6-2L': 18, '4d8+2-L': 26, '4d8-2-L': 22,
                 '10d4+2-2L': 34, '10d4-2-2L': 30}
        for roll in rolls:
            self.assertEqual(rulebook.roll_max(roll), rolls[roll])

