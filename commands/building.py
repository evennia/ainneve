"""
Building commands
"""

from .command import MuxCommand
from evennia import utils, CmdSet
from evennia.utils.evtable import EvTable
from evennia.prototypes.spawner import spawn
from evennia.utils.utils import inherits_from
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
        #self.add(CmdSpawn())
        self.add(CmdSetTraits())
        self.add(CmdSetSkills())
        self.add(CmdBuildShop())

#
# To use the prototypes with the @spawn function set
#   PROTOTYPE_MODULES = ["commands.prototypes"]
# Reload the server and the prototypes should be available.
#

class CmdSpawn(MuxCommand):
    """
    spawn objects from prototype

    Usage:
      @spawn
      @spawn[/switch] prototype_name
      @spawn[/switch] {prototype dictionary}

    Switch:
      noloc - allow location to be None if not specified explicitly. Otherwise,
              location will default to caller's current location.

    Example:
      @spawn GOBLIN
      @spawn {"key":"goblin", "typeclass":"monster.Monster", "location":"#2"}

    Dictionary keys:
      |wprototype  |n - name of parent prototype to use. Can be a list for
                        multiple inheritance (inherits left to right)
      |wkey        |n - string, the main object identifier
      |wtypeclass  |n - string, if not set, will use settings.BASE_OBJECT_TYPECLASS
      |wlocation   |n - this should be a valid object or #dbref
      |whome       |n - valid object or #dbref
      |wdestination|n - only valid for exits (object or dbref)
      |wpermissions|n - string or list of permission strings
      |wlocks      |n - a lock-string
      |waliases    |n - string or list of strings
      |wtraits     |n - dict of trait:value pairs to set on NPCs
      |wskills     |n - dict of skill:value pairs to set on NPCs
      |wndb_|n<name>  - value of a nattribute (ndb_ is stripped)
      any other keywords are interpreted as Attributes and their values.

    The available prototypes are defined globally in modules set in
    settings.PROTOTYPE_MODULES. If @spawn is used without arguments it
    displays a list of available prototypes.
    """

    key = "@spawn"
    aliases = ["spawn"]
    locks = "cmd:perm(spawn) or perm(Builders)"
    help_category = "Building"

    def func(self):
        "Implements the spawner"

        def _show_prototypes(prototypes):
            "Helper to show a list of available prototypes"
            string = "\nAvailable prototypes:\n %s"
            string %= utils.fill(", ".join(sorted(list(prototypes.keys()))))
            return string

        prototypes = spawn(return_parents=True)
        if not self.args:
            string = "Usage: @spawn {key:value, key, value, ... }"
            self.caller.msg(string + _show_prototypes(prototypes))
            return
        try:
            # make use of _convert_from_string from the SetAttribute command
            prototype = _convert_from_string(self, self.args)
        except SyntaxError:
            # this means literal_eval tried to parse a faulty string
            string = "|RCritical Python syntax error in argument. "
            string += "Only primitive Python structures are allowed. "
            string += "\nYou also need to use correct Python syntax. "
            string += "Remember especially to put quotes around all "
            string += "strings inside lists and dicts.|n"
            self.caller.msg(string)
            return

        if isinstance(prototype, str):
            # A prototype key
            keystr = prototype
            prototype = prototypes.get(prototype, None)
            if not prototype:
                string = "No prototype named '%s'." % keystr
                self.caller.msg(string + _show_prototypes(prototypes))
                return
        elif not isinstance(prototype, dict):
            self.caller.msg("The prototype must be a prototype key or a Python dictionary.")
            return

        if not "noloc" in self.switches and not "location" in prototype:
            prototype["location"] = self.caller.location

        # set the home of any prototypes to the location they were spawned
        if not "home" in prototype:
            prototype["home"] = prototype["location"]

        # overridden for Ainneve
        traits = prototype.pop('traits') if 'traits' in prototype else None
        skills = prototype.pop('skills') if 'skills' in prototype else None
        sdesc = prototype.pop('sdesc') if 'sdesc' in prototype else None

        for obj in spawn(prototype):
            if sdesc and hasattr(obj, 'sdesc'):
                obj.sdesc.add(sdesc() if callable(sdesc) else sdesc)

            if traits and hasattr(obj, 'traits'):
                for trait, value in traits.items():
                    trait = trait.upper()
                    if trait in obj.traits.all:
                        obj.traits[trait].base = value() if callable(value) else value

            if skills and hasattr(obj, 'skills'):
                for skill, value in skills.items():
                    skill = skill.lower()
                    if skill in obj.skills.all:
                        obj.skills[skill].base = value() if callable(value) else value

            self.caller.msg("Spawned %s." % obj.get_display_name(self.caller))


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
            for i in range(len(self.lhslist)):
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
             for i in range(3)]
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
            for i in range(len(self.lhslist)):
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
             for i in range(3)]
        table = EvTable(header=False, table=data)
        caller.msg(table)
