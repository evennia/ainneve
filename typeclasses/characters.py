"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# import importlib
from evennia import DefaultCharacter
from utils.trait import Trait

from world import races


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
            'strength': Trait('strength', static=True),
            'perception': Trait('perception', static=True),
            'intelligence': Trait('intelligence', static=True),
            'dexterity': Trait('dexterity', static=True),
            'charisma': Trait('charisma', static=True),
            'vitality': Trait('vitality', static=True),
            'magic': Trait('magic', static=True)
        }

        @property
        def strength(self):
            return self.db.primary_traits['strength'].current

        @strength.setter
        def strength(self, amount):
            self.db.primary_traits['strength'].base = amount

        @property
        def str(self):
            return self.strength

        @str.setter
        def str(self, amount):
            self.strength = amount

        # and so on, unless i think of a better way

        # Secondary Traits
        self.db.secondary_traits = {
            'health': Trait('health'),  # vit
            'stamina': Trait('stamina'),  # vit
            'skills': Trait('skills'),
            'languages': Trait('languages'),  # int
            # saves
            'fortitude': Trait('fortitude'),  # vit
            'reflex': Trait('reflex'),  # dex
            'will': Trait('will'),  # int
            # magic
            'mana': Trait('mana'),  # mag
            # armor
            'armor': Trait('armor', static=True)
        }

        self.db.slots = {}

    def become_race(self, race):
        """
        This method applies a race to the character.

        Args:
            race (str): Class path for the race

        Returns:
            bool: True if successful, False if otherwise
        """
        # set the race
        self.db.race = races.load_race(race)
        # load slots from the race
        for slot in self.db.race.slots:
            self.db.slots[slot] = None
