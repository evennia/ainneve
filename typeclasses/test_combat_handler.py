"""
Combat handler test module
"""

import re
from django.conf import settings
from mock import Mock
from evennia.utils.test_resources import EvenniaTest
from evennia.utils.spawner import spawn
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

