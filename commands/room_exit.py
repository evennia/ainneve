


from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.extended_room import CmdExtendedRoomLook
from evennia.contrib.extended_room import CmdExtendedRoomDesc
from evennia.contrib.extended_room import CmdExtendedRoomGameTime

class AinneveRoomExitsCmdSet(CmdSet):
    """Command set containing ExtendedRoom commands."""
    def at_cmdset_creation(self):
        # ExtendedRoom commands
        self.add(CmdExtendedRoomLook())
        self.add(CmdExtendedRoomDesc())
        self.add(CmdExtendedRoomGameTime())

        # Ainneve room builder commands
        self.add(CmdTerrain())
        self.add(CmdCapacity())

        # exit commands
        self.add(CmdStop())


class CmdTerrain(MuxCommand):
    """
    sets room terrain type

    Usage:
      @terrain [<room>] = <terrain>

    Notes:
      If <room> is omitted, defaults to your current location.

      Acceptable values for <terrain> are EASY, MODERATE, DIFFICULT,
      MUD, ICE, QUICKSAND, SNOW, VEGETATION, THICKET, or DEEPWATER.
    """
    key = "@terrain"
    locks = "cmd:perm(Builders)"
    help_category = 'Building'

    def func(self):
        """Set the property here."""
        if not self.rhs:
            self.caller.msg("Usage: @terrain [<room>] = <terrain>")
            return

        terrain = self.rhs.strip().upper()
        lhs = self.lhs.strip()
        if lhs != '':
            target = self.caller.search(lhs, global_search=True)
        else:
            target = self.caller.location

        if not target:
            self.caller.msg("Room not found.")
            return

        if target.is_typeclass('typeclasses.rooms.Room'):
            try:
                target.terrain = terrain
            except ValueError as e:
                self.caller.msg(e.message)
            else:
                self.caller.msg("Terrain type '{}' set on {}.".format(terrain,
                                                                  target.key))
        else:
            self.caller.msg('Cannot set terrain on {}.'.format(target.key))


class CmdCapacity(MuxCommand):
    """
    sets room's maximum capacity

    Usage:
      @capacity [<room>] = <maxchars>

    Args:
      room: the room on which to set the capacity
      maxchars: (positive int) maximum number of characters
                allowed in room or zero (0) for unlimited

    Notes:
      If <room> is omitted, defaults to your current location.
    """
    key = "@capacity"
    aliases = ["@cap"]
    locks = "cmd:perm(Builders)"
    help_category = 'Building'

    def func(self):
        """Set the property here."""
        if not self.rhs:
            self.caller.msg("Usage: @capacity [<room>] = <maxchars>")
            return

        try:
            capacity = int(self.rhs.strip())
        except ValueError:
            capacity = -1

        if capacity <= 0:
            self.caller.msg("Invalid capacity specified.")
            return

        lhs = self.lhs.strip()
        if lhs != '':
            target = self.caller.search(lhs,
                                        typeclass='typeclasses.rooms.Room',
                                        global_search=True)
        else:
            target = self.caller.location

        if not target:
            self.caller.msg("Room not found.")
            return

        target.db.max_chars = capacity
        self.caller.msg("Capacity set on {}.".format(target.get_display_name(self.caller)))


class CmdStop(MuxCommand):
    """
    stop moving

    Usage:
      stop

    Stops the current movement, if any.
    """
    key = "stop"

    def func(self):
        """
        This is a very simple command, using the
        stored deferred from the exit traversal above.
        """
        currently_moving = self.caller.ndb.currently_moving
        if currently_moving:
            currently_moving.cancel()
            del self.caller.ndb.currently_moving
            self.caller.msg("You stop moving.")
        else:
            self.caller.msg("You are not moving.")
