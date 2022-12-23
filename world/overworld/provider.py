import logging

from evennia.contrib.grid import wilderness
from evennia.prototypes.prototypes import search_prototype
from world.overworld import map

logger = logging.getLogger()


class OverworldMapProvider(wilderness.WildernessMapProvider):
    def is_valid_coordinates(self, wilderness, coordinates):
        """Returns True if coordinates is valid and can be walked to.

        Args:
            wilderness: the wilderness script
            coordinates (tuple): the coordinates to check as (x, y) tuple.

        Returns:
            bool: True if the coordinates are valid
        """
        in_lower_bound = super().is_valid_coordinates(wilderness, coordinates)
        if not in_lower_bound:
            return False

        x, y = coordinates
        if x >= map.OverworldMap.WIDTH:
            return False

        if y >= map.OverworldMap.HEIGHT:
            return False

        return True

    def get_location_name(self, coordinates):
        """
        Returns a name for the position at coordinates.

        Args:
            coordinates (tuple): the coordinates as (x, y) tuple.

        Returns:
            name (str)
        """
        location = map.OverworldMap.get(coordinates)
        name = location.name if location else "The wilderness"

        return name

    def at_prepare_room(self, coordinates, caller, room):
        """
        Called when a room gets activated for certain coordinates. This happens
        after every object is moved in it.
        This can be used to set a custom room desc for instance or run other
        customisations on the room.

        Args:
            coordinates (tuple): the coordinates as (x, y) where room is
                located at
            caller (Object): the object that moved into this room
            room (WildernessRoom): the room object that will be used at that
                wilderness location
        Example:
            An example use of this would to plug in a randomizer to show different
            descriptions for different coordinates, or place a treasure at a special
            coordinate.
        """

        location = map.OverworldMap.get(coordinates)
        prototype_name = location.room_prototype
        try:
            room_prototype = search_prototype(prototype_name, require_single=True)
            desc = room_prototype['desc']
        except KeyError:
            logger.error(f"No room prototype found with name {prototype_name} for overworld coordinates {coordinates}")
            desc = "Unknown"

        room.db.desc = desc

    @property
    def room_typeclass(self):
        # This is to avoid Circular Imports between Cmds, Typeclasses and the Provider
        from typeclasses.rooms import OverworldRoom

        return OverworldRoom

    @property
    def exit_typeclass(self):
        # This is to avoid Circular Imports between Cmds, Typeclasses and the Provider
        from typeclasses.exits import OverworldExit

        return OverworldExit
