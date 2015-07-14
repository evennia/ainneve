from evennia import CmdSet, utils
from evennia import Command

class SpellCmdSet(CmdSet):

    key = "spell_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        pass

# Add spell specific commands below
