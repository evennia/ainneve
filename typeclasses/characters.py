"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.contrib.rpsystem import ContribRPCharacter
from evennia.utils import lazy_property
from world.equip import EquipHandler
from world.traits import TraitHandler
from world.skills import apply_skills
from world.archetypes import Archetype
from world.death import CharDeathHandler, NPCDeathHandler


class Character(ContribRPCharacter):
    """Base character typeclass for Ainneve.

    This base Character typeclass should only contain things that would be
    common to NPCs, Mobs, Players, or anything else built off of it. Flags
    like "Aggro" would go further downstream.
    """
    def at_object_creation(self):
        super(Character, self).at_object_creation()
        self.db.race = None
        self.db.focus = None
        self.db.archetype = None

        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}
        self.db.position = 'STANDING'

        self.db.pose = self.db.pose or self.db.pose_default
        self.db.pose_death = 'lies dead.'

        # Non-persistent attributes
        self.ndb.group = None
        self.ndb.appr_lose = {}
        self.ndb.appr_win = {}

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

    def at_turn_start(self):
        """Hook called at the start of each combat turn or by a 6s ticker."""
        # refill traits that are allocated every turn
        self.traits.MV.fill_gauge()
        self.traits.BM.fill_gauge()
        self.traits.WM.fill_gauge()
        # Power Points are lost each turn
        self.traits.PP.reset_counter()

        if self.nattributes.has('combat_handler'):
            for _, item in self.equip:
                if item and hasattr(item, 'attributes') and \
                        item.attributes.has('combat_cmdset') and \
                        not self.cmdset.has_cmdset(item.db.combat_cmdset):
                    self.cmdset.add(item.db.combat_cmdset)

    def at_turn_end(self):
        """Hook called after turn actions are entered"""
        for _, item in self.equip:
            if item and hasattr(item, 'attributes') and \
                    item.attributes.has('combat_cmdset') and \
                    self.cmdset.has_cmdset(item.db.combat_cmdset):
                self.cmdset.remove(item.db.combat_cmdset)

    def at_death(self):
        """Hook called when a character dies."""
        self.scripts.add(CharDeathHandler)


class NPC(Character):
    """Base character typeclass for NPCs and enemies.
    """
    def at_object_creation(self):
        super(NPC, self).at_object_creation()

        self.db.slots = {'wield': None,
                         'armor': None}

        # initialize traits
        npc = Archetype()
        for key, kwargs in npc.traits.iteritems():
            self.traits.add(key, **kwargs)

        apply_skills(self)

    def at_death(self):
        """Hook called when an NPC dies."""
        self.scripts.add(NPCDeathHandler)
