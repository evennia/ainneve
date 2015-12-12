"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.utils import lazy_property
from world.equip import EquipHandler
from world.traits import TraitFactory
from world.economy import GC, SC, CC


class Character(DefaultCharacter):
    """Base character typeclass for Ainneve.

    This base Character typeclass should only contain things that would be
    common to NPCs, Mobs, Players, or anything else built off of it. Flags
    like "Aggro" would go further downstream.
    """
    def at_object_creation(self):
        self.db.race = None
        self.db.focus = None
        self.db.archetype = None

        self.db.slots = {}        # equipment slots
        self.db.limbs = ()        # limb/slot mappings

        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}

        # Non-persistent attributes
        self.ndb.group = None

    @property
    def traits(self):
        """TraitFactory that manages character traits."""
        return TraitFactory(self.db.traits)

    @property
    def skills(self):
        """TraitFactory that manages character traits."""
        return TraitFactory(self.db.skills)

    @lazy_property
    def equip(self):
        """Handler for equipped items."""
        return EquipHandler(self)

    @property
    def wealth(self):
        """Return the character's total wealth in CC."""
        wal = self.db.wallet
        return wal['GC'] * GC + wal['SC'] * SC + wal['CC'] + CC
