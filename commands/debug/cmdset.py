from commands.debug.encounters import CmdDebugSpawnEncounter
from commands.debug.overworld import CmdDebugEnterOverworld, CmdDebugOverworldTeleport
from evennia import CmdSet


class DebugCmdSet(CmdSet):
    """ Commands specific to debugging should be plugged here."""
    key = 'debug_cmdset'

    def at_cmdset_creation(self):
        self.add(CmdDebugEnterOverworld())
        self.add(CmdDebugOverworldTeleport())
        self.add(CmdDebugSpawnEncounter())
