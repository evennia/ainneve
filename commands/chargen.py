"""
Chargen commands.
"""
from evennia import CmdSet, Command
from evennia.utils.evmenu import EvMenu


class ChargenCmdSet(CmdSet):
    """Command set for the 'chargen' command."""
    key = "chargen_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(ChargenCmd())


class ChargenCmd(Command):
    """Launches the Chargen menu."""
    key = "chargen"

    def func(self):
        "Starts the chargen EvMenu instance"
        EvMenu(self.caller,
               "typeclasses.chargen",
               startnode="menunode_welcome_archetypes",
               allow_quit=True)
