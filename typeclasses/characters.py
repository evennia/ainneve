"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.contrib.rpsystem import ContribRPCharacter
from evennia.utils import lazy_property, utils
from world.equip import EquipHandler
from world.traits import TraitHandler
from world.skills import apply_skills
from world.archetypes import Archetype
from world.death import CharDeathHandler, NPCDeathHandler

from world.rulebook import skill_check


class Character(ContribRPCharacter):
    """Base character typeclass for Ainneve.

    This base Character typeclass should only contain things that would be
    common to NPCs, Mobs, Accounts, or anything else built off of it. Flags
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

    def at_pre_unpuppet(self):
        """Called just before beginning to un-connect a puppeting from
        this Account."""
        if self.nattributes.has('combat_handler'):
            self.ndb.combat_handler.remove_character(self)

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""

        # get description, build string
        name = self.get_display_name(looker)
        per  = self.traits.PER

        # These each do a skill check, but they always pass
        # if you're looking at yourself
        knows_race = skill_check(per) or looker == self
        knows_archetype = skill_check(per) or looker == self
        knows_health = skill_check(per) or looker == self
        knows_stamina = skill_check(per) or looker == self

        # this is the base name format - it just colors the name cyan
        string = "|c%s|n" % name

        # if we're adding race or archetype, add "the" after the name
        if (knows_race and self.db.archetype) or (knows_archetype and self.db.archetype):
            string += " the"

        if knows_race and self.db.race:
            string += " {}".format(self.db.race)
        if knows_archetype and self.db.archetype:
            string += " {}".format(self.db.archetype)

        # There may be a more efficient way to do this,
        # but we just want to add a period and a newline
        # after the name.
        string += ".\n"

        if knows_health:
            # traits.percent returns a string with a percent symbol
            # this is probably a silly idea, so maybe we should do a
            # PR in the future, but for now, we strip the symbol
            # and convert to a float
            health_percent = float(self.traits.HP.percent().strip('%'))
            if health_percent > .8:
                string += "They seem to be in good health.\n"
            elif health_percent > .5:
                string += "They seem a little roughed up.\n"
            # If we've not passed either previous condition, they could
            # have 0 health. Since we're converting to a float, it's possible
            # we won't get a float of zero, so we check HP.actual instead
            elif self.traits.HP.actual > 0:
                string += "They seem to be in pretty bad shape.\n"
            else:
                string += "They're dead.\n"

        if knows_stamina and self.traits.HP.actual > 0: # we check HP.actual,
                                                        # in case they're dead
            stamina_percent = float(self.traits.SP.percent().strip('%'))
            if stamina_percent > .8:
                string += "They seem full of energy.\n"
            elif stamina_percent > .5:
                string += "They look a bit tired.\n"
            else:
                string += "They look ready to fall over.\n"

        desc = self.db.desc
        if desc:
            string += "%s\n\n" % desc

        # self.equip.limbs is a dictionary of limbs and slots
        # the slots are things like armor and weild_1, while
        # the limbs are readable, like left arm and right arm
        limbs = self.equip.limbs

        # remember, when you do this with a dictionary, you're looping over
        # the keys in the dict.
        for limb in limbs:
            slots = limbs[limb] # since we just have a key to the dict, we use
                                # it to get the slot.

            for slot in slots:  # It's possible that a limb could have multiple slots
                item = self.equip.get(slot) # this returns None if there's no
                                            # item equipped
                if item:
                    key = item.get_display_name(looker)
                else:
                    key = 'Nothing'

                string += "|y{limb}|n: |w{name}|n\n".format(limb=limb, name=key)

        return string

class NPC(Character):
    """Base character typeclass for NPCs and enemies.
    """
    def at_object_creation(self):
        super(NPC, self).at_object_creation()

        self.db.emote_aggressive = "stares about angrily"

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

    def at_turn_start(self):
        """Hook called at the start of each combat turn."""
        super(NPC, self).at_turn_start()

        if "aggressive" in self.tags.all() and self.nattributes.has('combat_handler'):

            ch = self.ndb.combat_handler
            opponent = ch.db.characters[[cid for cid in ch.db.characters.keys()
                                    if cid != self.id][0]]

            if ch.get_range(opponent, self) != 'melee':
                ch.add_action('advance', self, opponent, 1)
            else:
                ch.add_action('attack', self, opponent, 1)

            ch.add_action('attack', self, opponent, 1)

    def at_turn_end(self):
        """Hook called at the end of each combat turn."""
        super(NPC, self).at_turn_end()

        if "aggressive" in self.tags.all() and self.nattributes.has('combat_handler'):
            if self.attributes.has('emote_aggressive'):
                self.execute_cmd("emote {}".format(self.db.emote_aggressive))
