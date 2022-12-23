"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.contrib.grid import wilderness
from evennia.objects.objects import DefaultRoom
from world.overworld import Overworld, OverworldMap

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    pass


class OverworldRoom(wilderness.WildernessRoom):
    """
    Special typeclass for the Overworld rooms
    Allows displaying the Overworld map
    """

    VIEW_WIDTH = 13
    VIEW_HEIGHT = 9
    VIEW_HALF_WIDTH = VIEW_WIDTH // 2
    VIEW_HALF_HEIGHT = VIEW_HEIGHT // 2

    def return_appearance(self, looker, **kwargs):
        result = super().return_appearance(looker, **kwargs)
        if not result:
            return result

        map = self.get_map_display(looker)
        result += f"\n{map}\n"

        return result

    def get_map_display(self, looker):
        overworld = Overworld.get_instance()
        x, y = overworld.get_obj_coordinates(looker)
        width = self.VIEW_WIDTH
        height = self.VIEW_HEIGHT
        half_width = self.VIEW_HALF_WIDTH
        half_height = self.VIEW_HALF_HEIGHT
        top_left_x = x - half_width
        top_left_y = y - half_height

        symbols = OverworldMap.get_rect_symbols(top_left_x, top_left_y, width, height)
        symbols[half_height][half_width] = "@"
        rows = ["".join((symbol for symbol in row)) for row in symbols]

        tile_str = "\n".join(rows)

        return tile_str