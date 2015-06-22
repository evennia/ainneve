"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import importlib
from evennia import DefaultCharacter
from ainneve.races import config as races_config
from ainneve.utils.trait import Trait

races_import_prefix = 'ainneve.races.'


class Character(DefaultCharacter):
    """
    This base Character typeclass should only contain things that would be
    common to NPCs, Mobs, Players, or anything else built off of it. Flags
    like "Aggro" would go further downstream.

    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    def at_object_creation(self):
        # race will be a separate Python class, defined and loaded from
        # some sort of configuration file
        self.db.race = None
        # same with Archetype, most likely
        self.db.archetype = None

        # Primary Traits
        self.db.primary_traits = {
            'str': Trait('strength', static=True),
            'per': Trait('perception', static=True),
            'int': Trait('intelligence', static=True),
            'dex': Trait('dexterity', static=True),
            'cha': Trait('charisma', static=True),
            'vit': Trait('vitality', static=True),
            'mag': Trait('magic', static=True)
        }

        @property
        def str(self):
            return self.db.primary_traits['str']

        @property
        def strength(self):
            return self.db.primary_traits['str']

        # and so on, unless i think of a better way

        # Secondary Traits
        self.db.secondary_traits = {
            'health': self.db.primary_traits['vit'],
            'stamina': self.db.primary_traits['vit'],
            'skills': Trait('skills'),
            'languages': self.db.primary_traits['int'],
            # saves
            'fortitude': self.db.primary_traits['vit'],
            'reflex': self.db.primary_traits['dex'],
            'willpower': self.db.primary_traits['int'],
            # magic
            'mana': self.db.primary_traits['mag'],
            # armor
            'armor': Trait('armor', static=True)
        }

        # Equipment
        self.db.weapons = {}
        self.db.equipment = {}

    def apply_race(self, race):
        if type(race) is str and race in races_config['races']:
            rpath = races_import_prefix + race.lower() + '.' + race.title()
            rmodule, rclass = rpath.rsplit('.', 1)
            rimp = importlib.import_module(rmodule)
            r = getattr(rimp, rclass)
            self.db.race = r()
        else:
            return False
