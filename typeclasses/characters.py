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
        race = self.db.race
        arch = self.db.archetype

        med = looker.skills.medicine.actual
        per = looker.traits.PER.actual

        # These each do a skill check, but they always pass
        # if you're looking at yourself
        knows_race = race and (skill_check(per, 3) or looker == self)
        knows_archetype = arch and (skill_check(per, 5) or looker == self)

        # these values may need to be tweaked - how difficult should each one be?
        knows_health_vague = skill_check(per, 4) or looker == self
        knows_health_exact = skill_check(med, 7) or looker == self

        knows_stamina_vague = skill_check(per, 6) or looker == self
        knows_stamina_exact = skill_check(med, 8) or looker == self

        # this is the base name format - it just colors the name cyan
        string = "|c%s|n" % name

        # if we're adding race or archetype, add "the" after the name
        if (knows_race) or (knows_archetype):
            string += " the"

        if knows_race:
            string += " {}".format(race)
        if knows_archetype:
            string += " {}".format(arch)

        # There may be a more efficient way to do this,
        # but we just want to add a period and a newline
        # after the name.
        string += ".\n"

        health_percent = float(self.traits.HP.percent().strip('%'))
        health_current = str(self.traits.HP.actual)
        health_max = str(self.traits.HP.max)

        if knows_health_vague or knows_health_exact:
            # traits.percent returns a string with a percent symbol
            # this is probably a silly idea, so maybe we should do a
            # PR in the future, but for now, we strip the symbol
            # and convert to a float
            if health_percent > .8:
                health_string = "They seem to be in good health."
            elif health_percent > .5:
                health_string = "They seem a little roughed up."
            # If we've not passed either previous condition, they could
            # have 0 health. Since we're converting to a float, it's possible
            # we won't get a float of zero, so we check HP.actual instead
            elif self.traits.HP.actual > 0:
                health_string = "They seem to be in pretty bad shape."
            else:
                health_string = "They're dead."

            if knows_health_exact:
                health_string += " HP {}/{}\n".format( health_current, health_max )
            else:
                health_string += "\n"
        # if we don't know their health, then just show a default message
        else:
            health_string = "They seem to be in good health.\n"

        string += health_string

        stamina_percent = float(self.traits.SP.percent().strip('%'))
        stamina_current = str(self.traits.SP.actual)
        stamina_max = str(self.traits.SP.max)
        stamina_string = ""

        # we check HP.actual, in case they're dead
        if health_current > 0 and (knows_stamina_vague or knows_stamina_exact):
            if stamina_percent > .8:
                stamina_string = "They seem full of energy."
            elif stamina_percent > .5:
                stamina_string = "They look a bit tired."
            else:
                stamina_string = "They look ready to fall over."

            if knows_stamina_exact:
                stamina_string += " SP {}/{}\n".format(stamina_current, stamina_max)
            else:
                stamina_string += "\n"

        string += stamina_string

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
