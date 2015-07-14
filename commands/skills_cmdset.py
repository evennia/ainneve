from evennia import CmdSet, utils
from evennia import Command

class SkillCmdSet(CmdSet):

    key = "skill_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdHide())
        self.add(CmdUnhide())

# Add skill specific commands below

class CmdHide(Command):
    """
    hide

    Usage:
      hide

    Allows a player to hide

    """
    key = "hide"
    #locks = "cmd:all()"
    locks = "cmd:has_skill(hide)"

    def func(self):
        caller = self.caller
        if caller.ndb.hidden:
            caller.msg("You are already hidden!")
            return

        # Display the msg to the caller
        caller.msg(caller.db.skills['hide'].msg_to_caller)
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
        caller = self.caller

        if not caller.ndb.hidden:
            caller.msg("You are not hidden!")
            return
        caller.msg("You step out of the shadows")
        caller.location.msg_contents("%s steps out of the shadows." %
                                     (caller.name.capitalize()),
                                     exclude=caller)
        caller.ndb.hidden = False