"""
Test module for combat actions.
"""
from mock import patch
from typeclasses.test_combat_handler import AinneveCombatTest
from utils.utils import call_immediate as CALL_IMMEDIATE
from world import rulebook
from server.conf import settings as ainneve_settings
from django.conf import settings


def _equip_item(char, item):
    """helper function: equips item on char"""
    item.move_to(char, quiet=True)
    item.at_get(char)
    char.equip.add(item)
    item.at_equip(char)


def _unequip_item(char, item):
    """helper function: unequips item on char"""
    item.at_remove(char)
    char.equip.remove(item)
    item.move_to(char.location, quiet=True)
    item.at_drop(char)


class AinneveCombatRangeTestCase(AinneveCombatTest):
    """Tests for range-related combat actions in Ainneve."""
    def setUp(self):
        super(AinneveCombatRangeTestCase, self).setUp()
        ch = self.script
        # set starting ranges
        ch.db.distances[frozenset((self.char2.id, self.obj1.id))] = 'reach'
        ch.db.distances[frozenset((self.char2.id, self.obj2.id))] = 'reach'
        ch.db.distances[frozenset((self.obj1.id, self.obj2.id))] = 'melee'

    def test_approach(self):
        """test approach combat action"""
        ch = self.script
        #####
        # approaching from ranged to melee
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_advance(0, self.char1, self.obj1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) advances to melee range with Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char advances to melee range with Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char advances to melee range with Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        # cleanup
        ch.move_character(self.char1, 'ranged')

        #####
        # approaching from ranged to reach
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_advance(0, self.char1, self.obj1, ['reach'])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) advances to reach range with Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char advances to reach range with Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char advances to reach range with Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        #####
        # approaching from ranged to reach
        # run action to test
        rulebook._do_advance(0, self.char1, self.obj1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) advances to melee range with Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char advances to melee range with Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char advances to melee range with Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        # cleanup
        ch.move_character(self.char1, 'ranged')

        #####
        # approaching from reach to reach
        ch.move_character(self.char1, 'reach', self.obj1)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        # run action to test
        rulebook._do_advance(0, self.char1, self.obj1, ['reach'])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) is already at reach with Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char is already at reach with Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char is already at reach with Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')

        # cleanup
        ch.move_character(self.char1, 'ranged')

        #####
        # invalid approach from melee to melee
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.obj2.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.char2.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_advance(0, self.char1, self.obj1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) is already at melee with Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char is already at melee with Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char is already at melee with Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        #####
        # invalid approach from reach from melee
        # using previous ranges; run action to test
        rulebook._do_advance(0, self.char1, self.obj1, ['reach'])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) cannot advance any farther on Obj(#4).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char cannot advance any farther on Obj.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, "< Char cannot advance any farther on Obj.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

    @patch('world.rulebook.std_roll', new=lambda: -10)
    def test_retreat_fail(self):
        """test invalid retreat and failure messaging"""
        ch = self.script
        #####
        # cannot retreat from ranged
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) has already retreated to ranged range.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char has already retreated to ranged range.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char has already retreated to ranged range.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        #####
        # test failure messaging for retreat from melee
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.obj2.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.char2.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attempts to retreat but stumbles and is unable.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char attempts to retreat but stumbles and is unable.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attempts to retreat but stumbles and is unable.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        # cleanup
        ch.move_character(self.char1, 'ranged')

        #####
        # test invalid retreat from reach to reach
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, ['reach'])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) has already retreated to reach range.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char has already retreated to reach range.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char has already retreated to reach range.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

    @patch('world.rulebook.std_roll', new=lambda: 10)
    def test_retreat_succ(self):
        """test retreat from reach"""
        ch = self.script
        # confirm starting ranges
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) retreats to ranged distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char retreats to ranged distance.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char retreats to ranged distance.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        #####
        # test success messaging for retreat from melee
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.obj2.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.char2.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) retreats to ranged distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char retreats to ranged distance.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char retreats to ranged distance.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

        #####
        # test success messaging for retreat melee to reach
        ch.db.distances[frozenset((self.char1.id, self.obj1.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.obj2.id))] = 'melee'
        ch.db.distances[frozenset((self.char1.id, self.char2.id))] = 'reach'
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')
        # run action to test
        rulebook._do_retreat(0, self.char1, self.char1, ['reach'])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) retreats to reach distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char retreats to reach distance.")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char retreats to reach distance.")
        # check ranges
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2),  'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj3),  'ranged')

    @patch('world.rulebook.std_roll', new=lambda: -10)
    def test_flee_fail(self):
        """test flee messaging when fleeing fails"""
        rulebook._do_flee(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) tries to escape, but is boxed in.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char tries to escape, but is boxed in.")

    @patch('world.rulebook.std_roll', new=lambda: 10)
    def test_flee_succ(self):
        """test flee messaging when fleeing succeeds"""
        # two-subturn action; run first subturn
        rulebook._do_flee(1, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) looks about frantically for an escape route.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char looks about frantically for an escape route.")

        # run second subturn
        rulebook._do_flee(0, self.char1, self.char1, [])
        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) seizes the opportunity to escape the fight!",
                               "Char(#6) knows they are safe, for a time..."])
        # check that the prompt was cleared on escape
        self.assertEqual(prompt.split('&')[-1], '')

        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char seizes the opportunity to escape the fight!")

        # check protection nattribute
        self.assertTrue(self.char1.nattributes.has('no_attack'))


class AinneveCombatItemTestCase(AinneveCombatTest):
    """Test case for item-related and miscellaneous combat actions."""
    def test_get_item(self):
        """test get item combat action"""
        # first time get succeeds and char1 gets the item
        rulebook._do_get(0, self.char1, self.melee, [])
        self.assertIn(self.melee, self.char1.contents)
        # second time get fails because already in char1.contents
        rulebook._do_get(0, self.char1, self.melee, [])
        # move an item out of the room and try to get
        self.ranged.move_to(self.room2, quiet=True)
        rulebook._do_get(0, self.char1, self.ranged, [])
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        expected = ["> Char(#6) gets a short sword(#8).",
                    "> Char(#6) searches around looking for a short sword(#8).",
                    "> Char(#6) searches around looking for a long bow(#10)."]
        self.assertEqual(msg, expected)
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        expected = [".. Char gets a short sword.",
                    ".. Char searches around looking for a short sword.",
                    ".. Char searches around looking for a long bow."]
        self.assertEqual(msg, expected)

    def test_drop_item(self):
        """test drop item combat action"""
        # fails when not holding item
        rulebook._do_drop(0, self.char1, self.melee, [])
        # succeeds when holding item
        self.melee.move_to(self.char1, quiet=True)
        self.melee.at_get(self.char1)
        rulebook._do_drop(0, self.char1, self.melee, [])
        self.assertIn(self.melee, self.room1.contents)
        # succeeds when item is equipped
        _equip_item(self.char1, self.melee)
        rulebook._do_drop(0, self.char1, self.melee, [])
        self.assertNotIn(self.melee, self.char1.equip)

        # check messaging
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        expected = ["> Char(#6) searches their bag, looking for a short sword(#8).",
                    "> Char(#6) drops a short sword(#8).",
                    "> Char(#6) drops a short sword(#8)."]
        self.assertEqual(msg, expected)

        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        expected = [".. Char searches their bag, looking for a short sword.",
                    ".. Char drops a short sword.",
                    ".. Char drops a short sword."]
        self.assertEqual(msg, expected)

    def test_equip_item(self):
        """test equip item combat action"""
        # should fail: can't equip from the floor
        rulebook._do_equip(0, self.char1, self.melee, [])
        self.assertNotIn(self.melee, self.char1.equip)
        # should succeed after moving item to char1
        self.melee.move_to(self.char1, quiet=True)
        self.melee.at_get(self.char1)
        rulebook._do_equip(0, self.char1, self.melee, [])
        self.assertIn(self.melee, self.char1.equip)
        # swap needlessly when you equip an already equipped item
        rulebook._do_equip(0, self.char1, self.melee, [])
        self.assertIn(self.melee, self.char1.equip)
        # should swap if equipping a different item
        self.ranged.move_to(self.char1, quiet=True)
        self.ranged.at_get(self.char1)
        rulebook._do_equip(0, self.char1, self.ranged, [])
        self.assertNotIn(self.melee, self.char1.equip)
        self.assertIn(self.ranged, self.char1.equip)

        # check messaging

        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        expected = ["> Char(#6) looks around, confused.",
                    "> Char(#6) equips a short sword(#8).",
                    "> Char(#6) removes a short sword(#8).",
                    "> Char(#6) equips a short sword(#8).",
                    "> Char(#6) removes a short sword(#8).",
                    "> Char(#6) equips a long bow(#10)."]
        self.assertEqual(msg, expected)

        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        expected = [".. Char looks around, confused.",
                    ".. Char equips a short sword.",
                    ".. Char removes a short sword.",
                    ".. Char equips a short sword.",
                    ".. Char removes a short sword.",
                    ".. Char equips a long bow."]
        self.assertEqual(msg, expected)

    def test_remove_item(self):
        """test the remove item combat action"""
        # fails when char1 doesn't have item
        rulebook._do_remove(0, self.char1, self.melee, [])
        # succeeds when char1 has item equipped
        _equip_item(self.char1, self.melee)
        rulebook._do_remove(0, self.char1, self.melee, [])
        self.assertNotIn(self.melee, self.char1.equip)
        self.assertIn(self.melee, self.char1.contents)
        # fails when char1 has item in inventory but not equipped
        rulebook._do_remove(0, self.char1, self.melee, [])

        # check messaging

        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        expected = ["> Char(#6) looks around, confused.",
                    "> Char(#6) removes a short sword(#8).",
                    "> Char(#6) looks around, confused."]
        self.assertEqual(msg, expected)

        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        expected = [".. Char looks around, confused.",
                    ".. Char removes a short sword.",
                    ".. Char looks around, confused."]
        self.assertEqual(msg, expected)

    def test_do_nothing(self):
        """test the 'nothing' combat action"""
        # no output when st_remaining > 0
        rulebook._do_nothing(1, self.char1, self.char1, [])
        # messaging when st_remaining == 0
        rulebook._do_nothing(0, self.char1, self.char1, [])

        # check messaging

        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) stares into space vacantly.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char stares into space vacantly.")


@patch('world.rulebook.utils.delay', new=CALL_IMMEDIATE)
class AinneveCombatAttackTestCase(AinneveCombatTest):
    """Tests for attack combat actions in Ainneve."""
    def setUp(self):
        super(AinneveCombatAttackTestCase, self).setUp()
        settings.PROTOTYPE_MODULES = ainneve_settings.PROTOTYPE_MODULES
        # It's possible we don't need to do this - however since we use
        # evennia.utils.spawner.spawn, we get an error if we don't.

    @patch('world.rulebook.std_roll', new=lambda: -3)
    def test_kick_fail(self):
        """test failing unarmed 'kick' attacks"""
        ch = self.script
        # confirm starting stat values
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        #####
        # kick fails at ranged range
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')

        # run both subturns of a kick action
        [rulebook._do_kick(st, self.char1, self.char2, []) for st in (1, 0)]

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) takes a step toward Char2(#7).",
                               "> Char(#6) is unable to kick Char2(#7)."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char takes a step toward Char2.",
                               "< Char is unable to kick Char2."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ["[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]",
                                  "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]"])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char takes a step toward Char2.",
                               ".. Char is unable to kick Char2."])
        #####
        # kick fails at reach distance
        ch.move_character(self.char1, 'reach', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')

        # run both subturns of a kick action
        [rulebook._do_kick(st, self.char1, self.char2, []) for st in (1, 0)]

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) takes a step toward Char2(#7).",
                               "> Char(#6) is unable to kick Char2(#7)."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char takes a step toward Char2.",
                               "< Char is unable to kick Char2."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ["[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]",
                                  "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]"])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char takes a step toward Char2.",
                               ".. Char is unable to kick Char2."])
        #####
        # test fail messaging for a kick at melee
        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')

        # run both subturns of a kick action
        [rulebook._do_kick(st, self.char1, self.char2, []) for st in (1, 0)]

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) takes a step toward Char2(#7).",
                               "> Char(#6) kicks toward Char2(#7) and misses."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char takes a step toward Char2.",
                               "< Char kicks toward Char2 and misses."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ["[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]",
                                  "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]"])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char takes a step toward Char2.",
                               ".. Char kicks toward Char2 and misses."])

        # final direct stat sanity check
        self.assertEqual(self.char2.traits.HP.actual, 10)
        self.assertEqual(self.char2.traits.SP.actual, 8)

    @patch('world.rulebook.std_roll', new=lambda: 0)
    def test_kick_succ(self):
        """test successful 'kick' attacks"""
        ch = self.script
        # confirm starting stat values
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        #####
        # test successful attack messaging for a kick
        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')

        # run both subturns of a kick action
        [rulebook._do_kick(st, self.char1, self.char2, []) for st in (1, 0)]

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) takes a step toward Char2(#7).",
                               "> Char(#6) kicks Char2(#7) savagely, sending them reeling."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char takes a step toward Char2.",
                               "< Char kicks Char2 savagely, sending them reeling."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ["[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]",
                                  "[ HP: 8 | WM: 0 | BM: 0 | SP: 8 ]"])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char takes a step toward Char2.",
                               ".. Char kicks Char2 savagely, sending them reeling."])
        #####
        # test successful attack messaging for a kick
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        # run both subturns of a kick action
        [rulebook._do_kick(st, self.char1, self.char2, ['subdue']) for st in (1, 0)]

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) takes a step toward Char2(#7).",
                               "> Char(#6) kicks Char2(#7) squarely in the chest, and Char2(#7) staggers from the blow."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char takes a step toward Char2.",
                               "< Char kicks Char2 squarely in the chest, and Char2 staggers from the blow."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ["[ HP: 8 | WM: 0 | BM: 0 | SP: 8 ]",
                                  "[ HP: 8 | WM: 0 | BM: 0 | SP: 6 ]"])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char takes a step toward Char2.",
                               ".. Char kicks Char2 squarely in the chest, and Char2 staggers from the blow."])

        # final direct stat check
        self.assertEqual(self.char2.traits.HP.actual, 8)
        self.assertEqual(self.char2.traits.SP.actual, 6)

    @patch('world.rulebook.std_roll', new=lambda: 0)
    def test_strike_fail(self):
        """test failing 'strike' attacks"""
        ch = self.script
        # confirm starting stat values
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        #####
        # strike attack fails at ranged
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) is too far away from Char2(#7) to strike them.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char is too far away from Char2 to strike them.")
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char is too far away from Char2 to strike them."])

        #####
        # strike attack fails at reach
        ch.move_character(self.char1, 'reach', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) is too far away from Char2(#7) to strike them.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char is too far away from Char2 to strike them.")
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char is too far away from Char2 to strike them."])

        #####
        # strike attack fails if no free hands
        _equip_item(self.char1, self.ranged)  # our bow is two-handed
        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        self.assertEqual(len(self.char1.equip), 2)
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) goes to punch, but does not have a free hand.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char goes to punch, but does not have a free hand.")
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char goes to punch, but does not have a free hand.")

        _unequip_item(self.char1, self.ranged)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # test failure messaging for strike at melee
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) attempts to punch Char2(#7) and misses.",
                               "> Char(#6) attempts to punch Char2(#7) and misses."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char attempts to punch Char2 and misses.",
                               "< Char attempts to punch Char2 and misses."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]',
                                  '[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char attempts to punch Char2 and misses.",
                               ".. Char attempts to punch Char2 and misses."])
        # final direct stat check
        self.assertEqual(self.char2.traits.HP.actual, 10)
        self.assertEqual(self.char2.traits.SP.actual, 8)

    @patch('world.rulebook.std_roll', new=lambda: 2)
    def test_strike_succ(self):
        """test successful 'strike' attacks"""
        ch = self.script
        # confirm starting stat values
        self.assertEqual(self.char2.traits.HP.actual, 10)
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) strikes Char2(#7) savagely with their fist.",
                               "> Char(#6) strikes Char2(#7) savagely with their fist."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char strikes Char2 savagely with their fist.",
                               "< Char strikes Char2 savagely with their fist."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 8 | WM: 0 | BM: 0 | SP: 8 ]',
                                  '[ HP: 6 | WM: 0 | BM: 0 | SP: 8 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char strikes Char2 savagely with their fist.",
                               ".. Char strikes Char2 savagely with their fist."])

        #####
        # 'subdue' style attack
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_strike(0, self.char1, self.char2, ['subdue'])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) strikes Char2(#7) hard in the chest, and Char2(#7) staggers from the blow.",
                               "> Char(#6) strikes Char2(#7) hard in the chest, and Char2(#7) staggers from the blow."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char strikes Char2 hard in the chest, and Char2 staggers from the blow.",
                               "< Char strikes Char2 hard in the chest, and Char2 staggers from the blow."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 6 | WM: 0 | BM: 0 | SP: 6 ]',
                                  '[ HP: 6 | WM: 0 | BM: 0 | SP: 4 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char strikes Char2 hard in the chest, and Char2 staggers from the blow.",
                               ".. Char strikes Char2 hard in the chest, and Char2 staggers from the blow."])

        #####
        # test single strike with only one hand free
        _equip_item(self.char1, self.melee)
        self.assertEqual(len(self.char1.equip), 1)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_strike(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        msg = msg.split('|')
        self.assertEqual(msg, ["> Char(#6) strikes Char2(#7) savagely with their fist."])
        msg, prompt = self.parse_msg_mock(self.char2)
        msg = msg.split('|')
        self.assertEqual(msg, ["< Char strikes Char2 savagely with their fist."])
        prompt = prompt.split('&')
        self.assertEqual(prompt, ['[ HP: 4 | WM: 0 | BM: 0 | SP: 4 ]'])
        msg, prompt = self.parse_msg_mock(self.obj1)
        msg = msg.split('|')
        self.assertEqual(msg, [".. Char strikes Char2 savagely with their fist."])

        # final direct stat sanity check
        self.assertEqual(self.char2.traits.HP.actual, 4)
        self.assertEqual(self.char2.traits.SP.actual, 4)

    @patch('world.rulebook.std_roll', new=lambda: -2)
    def test_attack_fail(self):
        """test unsuccessful attacks with weapons"""
        ch = self.script
        # confirm starting stat values
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        #####
        # attack fails with no weapon
        self.assertEqual(len(self.char1.equip), 0)
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) does not have a weapon that can attack opponents at ranged distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")

        ####
        # attack with melee weapon fails at ranged distance
        _equip_item(self.char1, self.melee)
        self.assertIn(self.melee, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) does not have a weapon that can attack opponents at ranged distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")

        # cleanup
        _unequip_item(self.char1, self.melee)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # attack with reach weapon fails at ranged distance
        _equip_item(self.char1, self.reach)
        self.assertIn(self.reach, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) does not have a weapon that can attack opponents at ranged distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at ranged distance.")

        # cleanup
        _unequip_item(self.char1, self.reach)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # attack with ranged weapon fails with no ammunition
        _equip_item(self.char1, self.ranged)
        self.assertIn(self.ranged, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) does not have any arrows in their quiver.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char does not have any arrows in their quiver.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char does not have any arrows in their quiver.")

        #####
        # test failure messaging for ranged weapon
        self.arrows.move_to(self.char1, quiet=True)
        self.arrows.at_get(self.char1)
        self.assertIn(self.ranged, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a long bow(#10) and misses.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a long bow and misses.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a long bow and misses.")

        #####
        # attack with ranged weapon fails at melee distance
        self.assertIn(self.ranged, self.char1.equip)
        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) does not have a weapon that can attack opponents at melee distance.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at melee distance.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char does not have a weapon that can attack opponents at melee distance.")

        # cleanup
        _unequip_item(self.char1, self.ranged)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # test failed attack messaging
        _equip_item(self.char1, self.melee)
        self.assertIn(self.melee, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a short sword(#8) and misses.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a short sword and misses.")
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a short sword and misses.")

        # cleanup
        _unequip_item(self.char1, self.melee)
        self.assertEqual(len(self.char1.equip), 0)

    @patch('world.rulebook.resolve_death')
    @patch('world.rulebook.std_roll', new=lambda: 0)
    def test_attack_succ(self, resolve_death_mock):
        """test successful attacks with weapons"""
        ch = self.script
        # confirm starting stat values
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(prompt, "[ HP: 10 | WM: 0 | BM: 0 | SP: 8 ]")

        #####
        # successful ranged attack
        _equip_item(self.char1, self.ranged)
        self.assertIn(self.ranged, self.char1.equip)
        self.arrows.move_to(self.char1, quiet=True)
        self.arrows.at_get(self.char1)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a long bow(#10), striking a painful blow.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a long bow, striking a painful blow.")
        self.assertEqual(prompt, "[ HP: 9 | WM: 0 | BM: 0 | SP: 8 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a long bow, striking a painful blow.")

        #####
        # successful ranged 'subdue' attack
        self.assertIn(self.ranged, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        rulebook._do_attack(0, self.char1, self.char2, ['subdue'])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) stuns Char2(#7) with a long bow(#10).")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char stuns Char2 with a long bow.")
        self.assertEqual(prompt, "[ HP: 9 | WM: 0 | BM: 0 | SP: 7 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char stuns Char2 with a long bow.")

        #####
        # successful ranged attack at reach distance
        self.assertIn(self.ranged, self.char1.equip)
        ch.move_character(self.char1, 'reach', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a long bow(#10), striking a painful blow.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a long bow, striking a painful blow.")
        self.assertEqual(prompt, "[ HP: 7 | WM: 0 | BM: 0 | SP: 7 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a long bow, striking a painful blow.")

        # cleanup
        _unequip_item(self.char1, self.ranged)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # successful reach attack
        _equip_item(self.char1, self.reach)
        self.assertIn(self.reach, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a pike polearm(#9), striking a painful blow.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a pike polearm, striking a painful blow.")
        self.assertEqual(prompt, "[ HP: 4 | WM: 0 | BM: 0 | SP: 7 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a pike polearm, striking a painful blow.")

        #####
        # successful reach attack at melee
        self.assertIn(self.reach, self.char1.equip)
        ch.move_character(self.char1, 'melee', self.char2)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a pike polearm(#9), striking a painful blow.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a pike polearm, striking a painful blow.")
        self.assertEqual(prompt, "[ HP: 1 | WM: 0 | BM: 0 | SP: 7 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a pike polearm, striking a painful blow.")

        # cleanup
        _unequip_item(self.char1, self.reach)
        self.assertEqual(len(self.char1.equip), 0)

        #####
        # successful melee attack
        _equip_item(self.char1, self.melee)
        self.assertIn(self.melee, self.char1.equip)
        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        rulebook._do_attack(0, self.char1, self.char2, [])

        # confirm messaging and stats prompt
        msg, prompt = self.parse_msg_mock(self.char1)
        self.assertEqual(msg, "> Char(#6) attacks Char2(#7) with a short sword(#8), striking a painful blow.")
        msg, prompt = self.parse_msg_mock(self.char2)
        self.assertEqual(msg, "< Char attacks Char2 with a short sword, striking a painful blow.")
        self.assertEqual(prompt, "[ HP: 0 | WM: 0 | BM: 0 | SP: 7 ]")
        msg, prompt = self.parse_msg_mock(self.obj1)
        self.assertEqual(msg, ".. Char attacks Char2 with a short sword, striking a painful blow.")
        # we lost poor char2
        self.assertTrue(resolve_death_mock.called)
