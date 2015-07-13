#
# Commands and cmdsetRelated to the equip handler
#
from evennia import CmdSet, utils
from evennia import Command

class AbilityCmdSet(CmdSet):

    key = "ability_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdHide())
        self.add(CmdUnhide())

class CmdHide(Command):
    """
    hide

    Usage:
      hide

    Allows a player to hide

    """
    key = "hide"
    locks = "cmd:all()"

    def func(self):
        "implements the command."

        caller = self.caller

        caller.msg(self.caller.inventory)

        if 'hide' not in caller.db.abilities:
            caller.msg("You don't know how to hide!")
            return

        if caller.ndb.hidden:
            caller.msg("You are already hidden!")
            return

        caller.msg("You meld into the shadows.")
        caller.location.msg_contents("%s melds into the shadows." % (caller.name.capitalize()),
                                     exclude=caller)
        caller.ndb.hidden = True

class CmdUnhide(Command):
    """
    unhide

    Usage:
      unhide

    Allows a player to unhide

    """
    key = "unhide"
    locks = "cmd:all()"

    def func(self):
        "implements the command."

        caller = self.caller

        if caller.ndb.hidden:
            caller.msg("You step out of the shadows")
            caller.location.msg_contents("%s steps out of the shadows." % (caller.name.capitalize()),
                                     exclude=caller)
            caller.ndb.hidden = False
            return

        caller.msg("You are not hidden!")

