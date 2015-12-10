"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# import importlib
from django.conf import settings
from evennia.utils import lazy_property

from objects import Object
from world.equip import EquipHandler
from world.traits import TraitHandler
from world.economy import GC, SC, CC


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
                      # no external commands can be called on char
                      "call:false()"]))
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def at_after_move(self, source_location):
        """
        We make sure to look around after a move.

        """
        self.execute_cmd('look')

    def at_pre_puppet(self, player, session=None):
        """
        This implementation recovers the character again after being "stowed
        away" to the `None` location in `at_post_unpuppet`.

        Args:
            player (Player): This is the connecting player.
            session (Session): Session controlling the connection.

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
                       sessid=session)

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

    def at_post_unpuppet(self, player, session=None):
        """
        We stove away the character when the player goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the player logged off ("headless", so to say).

        Args:
            player (Player): The player object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
        """
        if self.location:  # have to check, in case of multiple connections
            self.location.msg_contents("%s has left the game." % self.name,
                                       exclude=[self])
            self.db.prelogout_location = self.location
            self.location = None

    def at_object_creation(self):

        self.db.race = None
        self.db.focus = None
        self.db.archetype = None
        self.db.slots = {}        # equipment slots
        self.db.limbs = ()        # limb/slot mappings

        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}

        # Non-persistent attributes
        self.ndb.group = None

    @lazy_property
    def traits(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self)

    @lazy_property
    def skills(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self, db_attribute='skills')

    @lazy_property
    def equip(self):
        """Handler for equipped items."""
        return EquipHandler(self)

    @property
    def wealth(self):
        """Return the character's total wealth in CC."""
        wal = self.db.wallet
        return wal['GC'] * GC + wal['SC'] * SC + wal['CC'] + CC
