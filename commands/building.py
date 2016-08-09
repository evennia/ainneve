

from .command import MuxCommand
from evennia import utils, CmdSet
from evennia.utils.spawner import spawn
from evennia.commands.default.building import _convert_from_string


class AinneveBuildingCmdSet(CmdSet):
    """
    Implements Ainneve-specific buliding commands.
    """
    key = "AinneveBuilding"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"
        self.add(CmdSpawn())

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
            string = string % utils.fill(", ".join(sorted(prototypes.keys())))
            return string

        prototypes = spawn(return_prototypes=True)
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

        if isinstance(prototype, basestring):
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

        # overridden for Ainneve
        traits = prototype.pop('traits') if 'traits' in prototype else None
        skills = prototype.pop('skills') if 'skills' in prototype else None

        for obj in spawn(prototype):
            obj.sdesc.add(obj.key)
            if hasattr(obj, 'traits') and traits:
                for trait, value in traits.iteritems():
                    obj.traits[trait].base = value
            if hasattr(obj, 'skills') and skills:
                for skill, value in skills.iteritems():
                    obj.skills[skill].base = value

            self.caller.msg("Spawned %s." % obj.get_display_name(self.caller))

