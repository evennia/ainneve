from evennia import Command
from world.overworld import enter_overworld, Overworld


class CmdDebugEnterOverworld(Command):
    key = "debug__enter_overworld"

    locks = "cmd:perm(Admin) or perm(Developer)"
    help_category = "Debugging"

    def func(self):
        enter_overworld(self.caller)


class CmdDebugOverworldTeleport(Command):
    key = "debug__overworld_teleport"

    locks = "cmd:perm(Admin) or perm(Developer)"
    help_category = "Debugging"

    def func(self):
        caller = self.caller
        split_args = self.args.split()
        # TODO Make usage right
        arg_length = len(split_args)
        if not split_args or arg_length != 2:
            caller.msg("You must specify coordinates.\n"
                       "ex: debug__overworld_teleport 10 20")

        x, y = split_args
        try:
            x = int(x)
            y = int(y)
        except TypeError:
            caller.msg("Invalid teleport coordinates.")

        overworld = Overworld.get_instance()
        overworld.move_obj(caller, (x, y))
