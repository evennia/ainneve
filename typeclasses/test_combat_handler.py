"""
Combat handler test module
"""

import re
from django.conf import settings
from mock import Mock
from evennia.utils.test_resources import EvenniaTest
from evennia.prototypes.spawner import spawn
from evennia.utils import ansi, create
from server.conf import settings as ainneve_settings
from typeclasses.characters import Character, NPC
from typeclasses.rooms import Room
from typeclasses.combat_handler import CombatHandler
from utils.utils import sample_char

_RE = re.compile(r"^\+|-+\+|\+-+|--*|\|(?:\s|$)", re.MULTILINE)


class AinneveCombatTest(EvenniaTest):
    """Base test case for combat handler tests"""
    def setUp(self):
        settings.PROTOTYPE_MODULES = ainneve_settings.PROTOTYPE_MODULES
        self.character_typeclass = Character
        self.object_typeclass = NPC
        self.room_typeclass = Room
        self.script_typeclass = CombatHandler
        super(AinneveCombatTest, self).setUp()
        # create weapons for the fight
        self.melee = spawn({'prototype': 'SHORT_SWORD',
                            'location': self.room1},
                           prototype_modules=('world.content.prototypes_weapons',))[0]
        self.reach = spawn({'prototype': 'PIKE_POLEARM',
                            'location': self.room1},
                           prototype_modules=('world.content.prototypes_weapons',))[0]
        self.ranged = spawn({'prototype': 'LONG_BOW',
                             'location': self.room1},
                            prototype_modules=('world.content.prototypes_weapons',))[0]
        self.arrows = spawn({'prototype': 'ARROW_BUNDLE',
                             'location': self.room1},
                            prototype_modules=('world.content.prototypes_weapons',))[0]
        # set up chars
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        self.char1.traits.ATKM.base = self.char1.traits.ATKR.base = self.char1.traits.ATKU.base = 5
        sample_char(self.char2, 'warrior', 'human', 'cunning')
        self.char2.traits.HP.base = self.char2.traits.HP.current = 10
        # one additional NPC
        self.obj3 = create.create_object(self.object_typeclass, key="Obj3", location=self.room1, home=self.room1)

        # set sdescs to key for testing
        self.char1.sdesc.add(self.char1.key)
        self.char2.sdesc.add(self.char2.key)
        self.obj1.sdesc.add(self.obj1.key)
        self.obj2.sdesc.add(self.obj2.key)
        self.obj3.sdesc.add(self.obj3.key)
        # use mock msg methods
        self.char1.msg = Mock()
        self.char2.msg = Mock()
        self.obj1.msg = Mock()
        self.obj2.msg = Mock()
        self.obj3.msg = Mock()
        # add combatants
        self.script.add_character(self.char1)
        self.script.add_character(self.char2)
        self.script.add_character(self.obj1)
        self.script.add_character(self.obj2)
        self.script.add_character(self.obj3)

    @staticmethod
    def parse_msg_mock(char):
        """Separates text and prompt updates from a mocked msg."""
        msg = [args[0] if args else kwargs.get("text", "")
               for name, args, kwargs in char.msg.mock_calls]
        msg = "||".join(_RE.sub("", mess) for mess in msg if mess)
        msg = ansi.parse_ansi(msg, strip_ansi=True).strip()
        prompt = [kwargs.get("prompt", "") for name, args, kwargs
                  in char.msg.mock_calls if "prompt" in kwargs]
        prompt = "&".join(p for p in prompt)
        prompt = ansi.parse_ansi(prompt, strip_ansi=True).strip()
        char.msg.reset_mock()

        return msg, prompt


class AinneveCombatHandlerTestCase(AinneveCombatTest):
    """Test case for the Ainneve combat handler script."""

    def test_characters(self):
        """test adding and removing characters from a handler"""
        # the default script already has characters; create our own
        ch = create.create_script('typeclasses.combat_handler.CombatHandler', key="Script")

        self.assertEqual(len(ch.db.characters), 0)
        self.assertEqual(len(ch.db.action_count), 0)
        self.assertEqual(len(ch.db.turn_actions), 0)

        # add a character
        ch.add_character(self.char1)

        self.assertEqual(len(ch.db.characters), 1)
        self.assertEqual(len(ch.db.action_count), 1)
        self.assertEqual(len(ch.db.turn_actions), 1)
        self.assertEqual(len(ch.db.distances), 0)

        # add a second character (NPC)
        ch.add_character(self.obj1)

        self.assertEqual(len(ch.db.characters), 2)
        self.assertEqual(len(ch.db.action_count), 2)
        self.assertEqual(len(ch.db.turn_actions), 2)
        self.assertEqual(len(ch.db.distances), 1)

        self.assertIn(self.char1.id, ch.db.characters)
        self.assertIn(self.char1.id, ch.db.action_count)
        self.assertIn(self.char1.id, ch.db.turn_actions)

        self.assertIn(self.obj1.id, ch.db.characters)
        self.assertIn(self.obj1.id, ch.db.action_count)
        self.assertIn(self.obj1.id, ch.db.turn_actions)

        self.assertIn(frozenset((self.char1.id, self.obj1.id)), ch.db.distances)

        # remove the NPC; this ends the combat
        ch.remove_character(self.obj1)
        self.assertFalse(ch.is_valid())

    def test_actions(self):
        """test adding and removing combat actions"""
        ch = self.script

        # can't remove if there are no actions
        self.assertFalse(ch.remove_last_action(self.char1))

        # adding a single half turn action
        self.assertTrue(ch.add_action("advance", self.char1, self.obj1, 1))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 1)
        self.assertEqual(ch.db.action_count[self.char1.id], 1)

        # adding a free action doesn't increment `action_count`
        self.assertTrue(ch.add_action("drop", self.char1, self.melee, 0))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 2)
        self.assertEqual(ch.db.action_count[self.char1.id], 1)

        # adding a second half turn action
        self.assertTrue(ch.add_action("retreat", self.char1, self.char1, 1))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 3)
        self.assertEqual(ch.db.action_count[self.char1.id], 2)

        # adding a third isn't possible
        self.assertFalse(ch.add_action("advance", self.char1, self.obj1, 1))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 3)
        self.assertEqual(ch.db.action_count[self.char1.id], 2)

        # canceling the most recent action
        self.assertEqual(("retreat", self.char1), ch.remove_last_action(self.char1))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 2)
        self.assertEqual(ch.db.action_count[self.char1.id], 1)

        # adding a full-turn action on top of a half-turn action is allowed
        self.assertTrue(ch.add_action("kick", self.char1, self.char1, 2))
        self.assertEqual(len(ch.db.turn_actions[self.char1.id]), 3)
        self.assertEqual(ch.db.action_count[self.char1.id], 3)

    def test_range_and_movement(self):
        """test methods for working with combat range and movement"""
        ch = self.script

        # everyone starts at ranged from each other
        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # moving to reach with one opponent doesn't change range
        # with any other opponents
        ch.move_character(self.char1, 'reach', self.char2)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # moving another character obj1 to melee with char2 brings
        # it also to reach with char1, as it is already at reach with char2
        ch.move_character(self.obj1, 'melee', self.char2)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')  # <--
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # once again, moving a new character obj2 to reach with char1
        # only affects the range between them, and doesn't change
        # obj2's relationship with char2 or obj1
        ch.move_character(self.obj2, 'reach', self.char1)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # advancing char1 to melee with char2 also brings it to melee
        # with obj1 and moves to ranged with obj2
        ch.move_character(self.char1, 'melee', self.char2)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'melee')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # advancing to reach on a different char
        ch.move_character(self.char1, 'reach', self.obj2)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # retreating to reach from any who are too close
        ch.move_character(self.char1, 'reach')

        self.assertEqual(ch.get_range(self.char1, self.char2), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'reach')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'reach')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # advancing to melee takes on all the target's range relationships
        ch.move_character(self.char1, 'melee', self.obj3)

        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'ranged')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')  # <--
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'melee')  # <--
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

        # full retreat to ranged
        ch.move_character(self.char1, 'ranged')

        self.assertEqual(ch.get_range(self.char1, self.char2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj1), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char1, self.obj3), 'ranged')  # <--
        self.assertEqual(ch.get_range(self.char2, self.obj1), 'melee')
        self.assertEqual(ch.get_range(self.char2, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.char2, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj2), 'ranged')
        self.assertEqual(ch.get_range(self.obj1, self.obj3), 'ranged')
        self.assertEqual(ch.get_range(self.obj2, self.obj3), 'ranged')

    def test_get_proximity(self):
        """test the get_proximity method"""
        ch = self.script
        self.assertEqual(repr(ch.get_proximity(self.char1)),
                         "OrderedDict([('melee', []), ('reach', []), ('ranged', [5, 7, 12, 4])])")

        ch.move_character(self.obj1, 'melee', self.char2)
        ch.move_character(self.obj2, 'reach', self.char2)
        ch.move_character(self.char1, 'melee', self.char2)

        self.assertEqual(repr(ch.get_proximity(self.char1)),
                         "OrderedDict([('melee', [7, 4]), ('reach', [5]), ('ranged', [12])])")

