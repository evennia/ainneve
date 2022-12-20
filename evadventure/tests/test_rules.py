from unittest.mock import patch

from evennia.utils.test_resources import BaseEvenniaTest
from .. import rules


class TestEvAdventureRuleEngine(BaseEvenniaTest):

    def setUp(self):
        """Called before every test method"""
        super().setUp()
        self.roll_engine = rules.EvAdventureRollEngine()

    @patch("evadventure.rules.randint")
    def test_roll(self, mock_randint):
        mock_randint.return_value = 4
        self.assertEqual(self.roll_engine.roll("1d6"), 4)
        self.assertEqual(self.roll_engine.roll("2d6"), 2 * 4)
