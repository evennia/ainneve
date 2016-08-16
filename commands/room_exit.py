


from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.extended_room import *


class AinneveRoomExitsCmdSet(CmdSet):
    """Command set containing ExtendedRoom commands."""
    def at_cmdset_creation(self):
        # ExtendedRoom commands
        self.add(CmdExtendedLook())
        self.add(CmdExtendedDesc())
        self.add(CmdGameTime())

        # Ainneve room builder commands
        self.add(CmdTerrain())
        self.add(CmdRangeField())

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


class CmdRangeField(MuxCommand):
    """
    sets room's combat range field

    Usage:
      @rangefield [<room>] = (<length>, <width>)

    Args:
      room: the room on which to set the range field
      length: (positive int) length of the combat range field
      width: (positive int) width of the combat range field; limits
        the number of characters that may stand abreast in the room

    Notes:
      If <room> is omitted, defaults to your current location.
    """
    key = "@rangefield"
    locks = "cmd:perm(Builders)"
    help_category = 'Building'

    def func(self):
        """Set the property here."""
        if not self.rhs:
            self.caller.msg("Usage: @rangefield [<room>] = (<length>, <width>)")
            return

        # range_field has to be set as a tuple; parse the string input
        rf_re = re.compile(r'(?:\(\s*(\d+)\s*,\s*(\d+)\s*\)|^\s*(\d+)\s*,\s*(\d+)\s*$)', re.UNICODE)
        rf_match = rf_re.search(self.rhs)

        if rf_match:
            range_field = tuple(sorted((int(x) for x in rf_match.groups()
                                        if x is not None),
                                       reverse=True))
        else:
            self.caller.msg("Invalid range field specified.")
            return

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
                target.range_field = range_field
            except ValueError as e:
                self.caller.msg(e.message)
            else:
                self.caller.msg("Range field set on {}.".format(target.key))
        else:
            self.caller.msg('Cannot set range field on {}.'.format(target.key))



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
