"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# import importlib
from evennia.utils import lazy_property
from world.traits.trait import Trait
from world import races
from world.equip import EquipHandler
from objects import Object
from django.conf import settings
from world.databases.traits_db import primary_trait_db, secondary_trait_db
from world.databases.spell_db import spell_db
from world.databases.skill_db import skill_db

class Character(Object):
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

    def basetype_setup(self):
        """
        Setup character-specific security.

        You should normally not need to overload this, but if you do,
        make sure to reproduce at least the two last commands in this
        method (unless you want to fundamentally change how a
        Character object works).

        """
        super(Character, self).basetype_setup()
        self.locks.add(
            ";".join(["get:false()",  # noone can pick up the character
                      "call:false()"]))  # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def at_after_move(self, source_location):
        """
        We make sure to look around after a move.

        """
        self.execute_cmd('look')

    def at_pre_puppet(self, player, sessid=None):
        """
        This implementation recovers the character again after having been "stoved
        away" to the `None` location in `at_post_unpuppet`.

        Args:
            player (Player): This is the connecting player.
            sessid (int): Session id controlling the connection.

        """
        if self.db.prelogout_location:
            # try to recover
            self.location = self.db.prelogout_location
        if self.location is None:
            # make sure location is never None (home should always exist)
            self.location = self.home
        if self.location:
            # save location again to be sure
            self.db.prelogout_location = self.location
            self.location.at_object_receive(self, self.location)
        else:
            player.msg("{r%s has no location and no home is set.{n" % self,
                       sessid=sessid)

    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.msg("\nYou become {c%s{n.\n" % self.name)
        self.execute_cmd("look")
        if self.location:
            self.location.msg_contents("%s has entered the game." % self.name,
                                       exclude=[self])

    def at_post_unpuppet(self, player, sessid=None):
        """
        We stove away the character when the player goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the player logged off ("headless", so to say).

        Args:
            player (Player): The player object that just disconnected
                from this object.
            sessid (int): Session id controlling the connection that
                just disconnected.
        """
        if self.location:  # have to check, in case of multiple connections closing
            self.location.msg_contents("%s has left the game." % self.name,
                                       exclude=[self])
            self.db.prelogout_location = self.location
            self.location = None

    def at_object_creation(self):
        # race will be a separate Python class, defined and loaded from
        # some sort of configuration file
        self.db.race = None
        # same with Archetype, most likely
        self.db.archetype = None

        # each player will be assigned with ability points
        self.db.ability_points = 100

        # each player will be assigned all skills [skill_db.py]
        self.db.skills = skill_db
        # each player will be assigned all spells [spell_db.py]
        self.db.spells = spell_db

        #each player will be assigned all primary traits [traits_db.py]
        self.db.primary_traits = primary_trait_db
        #each player will be assigned all secondary traits [traits_db.py]
        self.db.secondary_traits = secondary_trait_db

        self.ndb.group = None

    @property
    def inventory(self):
        """
        Return inventory items.
        """
        eq = hasattr(self, 'equip') and self.equip.items or []
        return [obj for obj in self.contents if obj not in eq]

    @lazy_property
    def equip(self):
        """
        An handler to administrate characters equipment.
        """
        # sample slots, when race is completed feed race.slots instead
        slots = ('head', 'torso', 'neck1', 'neck2', 'feet')
        return EquipHandler(self, slots=slots)

    # helper method, checks if stat is valid
    def find_stat(self, stat):
        if stat in self.db.primary_traits:
            return self.db.primary_traits[stat]
        elif stat in self.db.secondary_traits:
            return self.db.secondary_traits[stat]
        else:
            return None

    # helper method, checks if race gets extra language points
    def determine_language_points(self):
        if self.bonuses['languages']:
            return self.bonuses['languages']
        else:
            return 0

    def base_stat(self, stat, amount):
        # sets the secondary traits
        if stat == 'vitality':
            for secondary in ['health', 'stamina', 'fortitude', 'reflex']:
                self.db.secondary_traits[secondary].base = amount

        if stat == 'intelligence':
            bonus_language_points = self.determine_language_points()
            self.db.secondary_traits[
                'languages'] = amount + bonus_language_points
            self.db.secondary_traits['will'] = amount

        # as per the OA blue rulebook mana can never exceed 10 (page 49)
        if stat == 'mana':
            if (self.db.secondary_traits['mana'].base + amount) >= 10:
                self.db.secondary_traits['mana'].base = 10
                self.mod_stat(stat, self.db.secondary_traits['mana'].mod)
                return
            else:
                self.db.secondary_traits['mana'].base += amount
                self.mod_stat(stat, self.db.secondary_traits['mana'].mod)
                return

        valid_stat = self.find_stat(stat)
        if valid_stat:
            valid_stat.base = amount
        else:
            return False

    def mod_stat(self, stat, amount):
        # as per the OA blue rulebook mana can never exceed 10 (page 49)
        if stat == 'mana':
            if (self.db.secondary_traits['mana'].base + amount) > 10:
                self.db.secondary_traits['mana'].mod = 10 - \
                                                       self.db.secondary_traits[
                                                           'mana'].base
                return
            elif (self.db.secondary_traits['mana'].base +
                      self.db.secondary_traits['mana'].mod + amount) > 10:
                self.db.secondary_traits[
                    'mana'
                ].mod = 10 - (self.db.secondary_traits['mana'].base +
                              self.db.secondary_traits['mana'].mod)
                return
            else:
                self.db.secondary_traits['mana'].mod = amount
                return

        valid_stat = self.find_stat(stat)
        if valid_stat:
            valid_stat.base = amount
        else:
            return False

    def get_stat(self, stat):
        valid_stat = self.find_stat(stat)
        if valid_stat:
            return valid_stat
        else:
            return None

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

    def has_skill(self, skill):
        if skill in self.db.skills:
            return True

    def has_spell(self, spell):
        if spell in self.db.spells:
            return True

    def get_skill(self,skill):
        return self.db.skills[skill]

    def get_spell(self,spell):
        return self.db.spells[spell]




