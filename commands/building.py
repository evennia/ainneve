"""
Building commands
"""

from .command import MuxCommand
from evennia import utils, CmdSet
from evennia.utils.evtable import EvTable
from evennia.utils.utils import inherits_from
from evennia.commands.default.building import CmdSpawn as DefaultCmdSpawn
from evennia.commands.default.building import _convert_from_string
from world.archetypes import ALL_TRAITS
from world.skills import ALL_SKILLS
from typeclasses.npcshop.npcshop import CmdBuildShop


class AinneveBuildingCmdSet(CmdSet):
    """
    Implements Ainneve-specific building commands.
    """
    key = "AinneveBuilding"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"
        self.add(CmdSpawn())
        self.add(CmdSetTraits())
        self.add(CmdSetSkills())
        self.add(CmdBuildShop())

#
# To use the prototypes with the @spawn function set
#   PROTOTYPE_MODULES = ["commands.prototypes"]
# Reload the server and the prototypes should be available.
#

class CmdSpawn(DefaultCmdSpawn):
    def func(self):
        """
        "Implements the spawner"

        # overridden for Ainneve
        #
        # TODO FIXME this used to fully cut-n-paste/extend the old spawner,
        # but really it should just tack on any traits/skills/sdec found in the
        #   generated prototype object
        # For now, assume that the spawner already creates them.
        # The rest of this string'd-out code is for posterity to show what it used to do.
        #
        traits = prototype.pop('traits') if 'traits' in prototype else None
        skills = prototype.pop('skills') if 'skills' in prototype else None
        sdesc = prototype.pop('sdesc') if 'sdesc' in prototype else None

        for obj in spawn(prototype):
            if sdesc and hasattr(obj, 'sdesc'):
                obj.sdesc.add(sdesc() if callable(sdesc) else sdesc)
            
            if traits and hasattr(obj, 'traits'):
                for trait, value in traits.iteritems():
                    trait = trait.upper()
                    if trait in obj.traits.all:
                        obj.traits[trait].base = value() if callable(value) else value

            if skills and hasattr(obj, 'skills'):
                for skill, value in skills.iteritems():
                    skill = skill.lower()
                    if skill in obj.skills.all:
                        obj.skills[skill].base = value() if callable(value) else value

            self.caller.msg("Spawned %s." % obj.get_display_name(self.caller))
        """
        return super().func()



class CmdSetTraits(MuxCommand):
    """
    examine or set traits on an NPC

    Usage
      @traits <npc> [trait_name[,trait_name..][ = value[,value..]]]

    Displays all traits if no trait_name is specified.

    Displays current values of named trait(s) if no equal sign or assignment
    values are used.

    Assigning values to traits with the equal sign requires that the
    same number of trait_name and value items be present on each side of the
    equal sign. The first trait named is assigned the first value, the second
    trait assigned the second value, and so on. Trait values must be between
    0 and 10.

    Valid trait_name s are

    STR - Strength          DEX - Dexterity
    PER - Perception        CHA - Charisma
    INT - Intelligence      VIT - Vitality

    MAG - Magic  (BM + WM = MAG)
      BM  - Black Magic
      WM  - White Magic

    HP - Health Points      MV - Movement Points
    SP - Stamina Points

    ATKM - Melee Attack     DEF - Defense
    ATKR - Ranged Attack    PP  - Power Points
    ATKU - Unarmed Attack
    """

    key = "@traits"
    aliases = ["@trait", "@tr"]
    locks = "cmd:perm(edit_npc) or perm(Builders)"
    help_category = "Building"

    def _usage(self):
        self.caller.msg('Usage: @traits <npc> [trait[,trait..][ = value[,value..]]]')
        self.caller.msg('Valid Traits: STR PER INT DEX CHA VIT MAG BM WM')
        self.caller.msg('              HP SP MV ATKM ATKR ATKU DEF PP')

    def _format_trait_3col(self, trait):
        """Return a trait : value pair formatted for 3col layout"""
        return "|C{:<17.17}|n : |w{:>4}|n".format(
                    trait.name, trait.actual)

    def func(self):
        caller = self.caller

        if not self.args:
            self._usage()
            return

        # split off the target from the first item of lhslist
        targs = tuple(self.lhslist[0].rsplit(' ', 1))
        if len(targs) == 1 or \
                (len(targs) > 1 and targs[1].upper() not in ALL_TRAITS):
            target, self.lhslist[0] = self.lhslist[0], ''
        else:
            target, self.lhslist[0] = targs

        # search for the target NPC
        char = caller.search(target,
                             location=caller.location,
                             typeclass='typeclasses.characters.NPC')

        if not char:
            return

        # the inherits_from check below is necessary due to an issue
        # with search() on the ContripRPObject class
        if not inherits_from(char, 'typeclasses.characters.NPC'):
            caller.msg("Could not find NPC: '{}'".format(target))
            return

        if self.rhs:
            if not all((x.isdigit() for x in self.rhslist)):
                caller.msg('Assignment values must be numeric.')
                return
            if len(self.lhslist) != len(self.rhslist):
                caller.msg('Incorrect number of assignment values.')
                return
            for i in list(range(len(self.lhslist))):
                if self.lhslist[i].upper() in char.traits.all:
                    char.traits[self.lhslist[i].upper()].base = \
                        min(max(int(self.rhslist[i]), 0), 10)
                    caller.msg('Trait "{}" set to {} for {}'.format(
                        self.lhslist[i].upper(),
                        min(max(int(self.rhslist[i]), 0), 10),
                        char.sdesc.get()))
                else:
                    caller.msg('Invalid trait: "{}"'.format(self.lhslist[i]))

        # display traits
        data = []
        if any(self.lhslist):
            traits = [t.upper() for t in self.lhslist
                      if t.upper() in char.traits.all]
        else:
            traits = char.traits.all

        if len(traits) == 0:
            return
        elif 0 < len(traits) < 3:
            [data.append([self._format_trait_3col(char.traits[t])])
             for t in traits]
        else:
            [data.append([self._format_trait_3col(char.traits[t])
                          for t in traits[i::3]])
             for i in list(range(3))]
        table = EvTable(header=False, table=data)
        caller.msg(table)


class CmdSetSkills(MuxCommand):
    """
    examine or set traits on an NPC

    Usage
      @skills <npc> [skill_name[,skill_name..][ = value[,value..]]]

    Displays all current skill values if no skill_name is specified.

    Displays current values of named skill(s) if no equal sign or assignment
    values are used.

    Assigning values to skills with the equal sign requires that the
    same number of skill_name and value items be present on each side of the
    equal sign. The first skill named is assigned the first value, the second
    skill assigned the second value, and so on. Skill values must be between
    0 and 10.

    Valid skill_name s are

    escape      climb       jump
    lockpick    listen      sense
    appraise    medicine    survival
    balance     sneak       throwing
    animal      barter      leadership
    """

    key = "@skills"
    aliases = ["@skill", "@sk"]
    locks = "cmd:perm(edit_npc) or perm(Builders)"
    help_category = "Building"

    def _usage(self):
        self.caller.msg('Usage: @skills <npc> [skill[,skill..][ = value[,value..]]]')
        self.caller.msg('Valid Skills: escape climb jump lockpick listen sense')
        self.caller.msg('              appraise medicine survival balance sneak')
        self.caller.msg('              throwing animal barter leadership')

    def _format_skill_3col(self, skill):
        """Return a skill : value pair formatted for 3col layout"""
        return "|M{:<17.17}|n : |w{:>4}|n".format(
                    skill.name, skill.actual)

    def func(self):
        caller = self.caller

        if not self.args:
            self._usage()
            return

        # split the target off from the first list argument
        targs = tuple(self.lhslist[0].rsplit(' ', 1))
        if len(targs) == 1 or \
                (len(targs) > 1 and targs[1].lower() not in ALL_SKILLS):
            target, self.lhslist[0] = self.lhslist[0], ''
        else:
            target, self.lhslist[0] = targs

        char = caller.search(target,
                             location=caller.location,
                             typeclass='typeclasses.characters.NPC')

        if not char:
            return

        # the inherits_from check below is necessary due to an issue
        # with search() on the ContripRPObject class
        if not inherits_from(char, 'typeclasses.characters.NPC'):
            caller.msg("Could not find NPC: '{}'".format(target))
            return

        if self.rhs:  # handle assignments
            if not all((x.isdigit() for x in self.rhslist)):
                caller.msg('Assignment values must be numeric.')
                return
            if len(self.lhslist) != len(self.rhslist):
                caller.msg('Incorrect number of assignment values.')
                return
            for i in list(range(len(self.lhslist))):
                if self.lhslist[i].lower() in char.skills.all:
                    char.skills[self.lhslist[i].lower()].base = \
                        min(max(int(self.rhslist[i]), 0), 10)  # enforce {0, 10} bounds
                    caller.msg('Skill "{}" set to {} for {}'.format(
                        self.lhslist[i].lower(),
                        min(max(int(self.rhslist[i]), 0), 10),
                        char.sdesc.get()))
                else:
                    caller.msg('Invalid skill: "{}"'.format(self.lhslist[i]))

        # display traits
        data = []
        if any(self.lhslist):
            skills = [s.lower() for s in self.lhslist
                      if s.lower() in char.skills.all]
        else:
            skills = char.skills.all

        if len(skills) < 3:
            [data.append([self._format_skill_3col(char.skills[s])])
             for s in skills]
        else:
            [data.append([self._format_skill_3col(char.skills[s])
                          for s in skills[i::3]])
             for i in list(range(3))]
        table = EvTable(header=False, table=data)
        caller.msg(table)
