


from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.extended_room import *

from utils.utils import doc

from typeclasses import maps, rooms

class AinneveRoomExitsCmdSet(CmdSet):
    """Command set containing ExtendedRoom commands."""
    def at_cmdset_creation(self):
        # ExtendedRoom commands
        self.add(CmdExtendedLook())
        self.add(CmdExtendedDesc())
        self.add(CmdGameTime())

        # Ainneve room builder commands
        self.add(CmdZone())
        self.add(CmdTerrain())
        self.add(CmdMapTile())
        self.add(CmdCapacity())

        # exit commands
        self.add(CmdStop())


class ModifyRoomCommand(MuxCommand):
    locks = "cmd:perm(Builders)"
    help_category = 'Building'
    success_msg = "rhs: {}, target.key: {}"
    failure_msg = "target.key: {}"

    def func(self):
        if not self.rhs:
            arg_name = self.key.replace('@', '', 1).replace('_', ' ')
            self.caller.msg("Usage: {} [<room>] = <{}>".format(self.key, arg_name))
            return

        lhs = self.lhs.strip()
        if lhs != '':
            target = self.caller.search(lhs, global_search=True)
        else:
            target = self.caller.location

        if not target:
            self.caller.msg("Room not found.")
            return

        if target.is_typeclass('typeclasses.rooms.Room', False):
            try:
                success = self.modify(target)
                if success == False: # None is falsy
                    # modify() should display errors as needed
                    return
            except ValueError as e:
                self.caller.msg(e.message)
            else:
                self.caller.msg(self.success_msg.format(self.rhs,
                                                        target.key))
        else:
            self.caller.msg(self.failure_msg.format(target.key))

    def modify(self, target):
        """
        Modify the target as needed, using self.rhs for reference.
        """
        raise NotImplementedError()

terrain_types = sorted(rooms.Room._TERRAINS.keys())
@doc("""
sets room terrain type

Usage:
  @terrain [<room>] = <terrain>

Notes:
  If <room> is omitted, defaults to your current location.

  Acceptable values for <terrain> are:
   - {}
""".format('\n   - '.join(terrain_types)))
class CmdTerrain(ModifyRoomCommand):
    key = "@terrain"
    success_msg = "Terrain type '{}' set on {}."
    failure_msg = "Cannot set terrain on {}."

    def modify(self, target):
        """Set the property here."""
        self.rhs = self.rhs.strip().upper()
        target.terrain = self.rhs


class CmdMapTile(ModifyRoomCommand):
    """
    sets the map tile for a room

    Usage:
      @map_tile [<room>] = <map tile>

    Notes:
      If <room> is omitted, defaults to your current location.

      map_tile is a three-character string that represents this room on the map.

      Many rooms, such as roads, will generate their own tiles as needed.
      Some terrain types have default map tiles, too.
    """
    key = "@map_tile"
    success_msg = "Map tile '{}' set on {}."
    failure_msg = "Cannot set map tile on {}."

    def modify(self, target):
        """Set the property here."""
        self.rhs = self.rhs.strip()

        # this allows tiles like ' x '
        if len(self.rhs) == 5 and self.rhs[0] in '\'"' and self.rhs[-1] in '\'"':
            self.rhs = self.rhs[1:-1] # drop the quotes

        if len(self.rhs) != maps.CELL_WIDTH:
            self.caller.msg("Map tile '{}' must be {} characters long".format(
                self.rhs,
                maps.CELL_WIDTH
            ))
            return False

        target.db.map_tile = self.rhs

class CmdZone(ModifyRoomCommand):
    """
    sets the zone for a room

    Usage:
      @zone [<room>] = <zone>

    Notes:
      If <room> is omitted, defaults to your current location.

      zone is a string that represents the zone of the world map
      that the room is in.
    """
    key = "@zone"
    locks = "cmd:perm(tag) or perm(Builders)"
    success_msg = "Zone '{}' set on {}."
    failure_msg = "Cannot set zone on {}."

    def modify(self, target):
        """Set the property here."""
        target.tags.clear(category="zone")
        target.tags.add(self.rhs.strip(), category="zone")


class CmdCapacity(ModifyRoomCommand):
    """
    sets room's maximum capacity

    Usage:
      @capacity [<room>] = <capacity>

    Args:
      room: the room on which to set the capacity
      capacity: (positive int) maximum number of characters
                allowed in room or zero (0) for unlimited

    Notes:
      If <room> is omitted, defaults to your current location.
    """
    key = "@capacity"
    aliases = ["@cap"]
    success_msg = "Capacity {} set on {}."
    failure_msg = "Cannot set capacity on {}."

    def modify(self, target):
        """Set the property here."""
        try:
            self.rhs = int(self.rhs.strip())
        except ValueError:
            self.rhs = -1

        if self.rhs <= 0:
            self.caller.msg("Invalid capacity specified.")
            return False

        target.db.max_chars = self.rhs
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
