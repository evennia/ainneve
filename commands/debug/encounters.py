from commands.command import Command
from world.encounters.data import ENCOUNTER_GOBLIN_SCOUTS


class CmdDebugSpawnEncounter(Command):
    key = "debug__spawn_encounter"

    locks = "cmd:perm(Admin) or perm(Developer)"
    help_category = "Debugging"

    def func(self):
        ENCOUNTER_GOBLIN_SCOUTS.spawn(location=self.caller.location, players=[self.caller])
