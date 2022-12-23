"""
Tests of the utils module.

"""

from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from world import utils
from typeclasses.objects import Object


class TestUtils(BaseEvenniaTest):
    def test_get_obj_stats(self):

        obj = create.create_object(
            Object, key="testobj", attributes=(("desc", "A test object"),)
        )
        result = utils.get_obj_stats(obj)

        self.assertEqual(
            result,
            """
|ctestobj|n
Value: ~|y0|n coins

A test object

Slots: |w1|n, Used from: |wbackpack|n
Quality: |wN/A|n, Uses: |wuses|n
Attacks using |wNo attack|n against |wNo defense|n
Damage roll: |wNone|n
""".strip(),
        )
