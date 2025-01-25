"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.contrib.grid import wilderness
from evennia.contrib.grid.xyzgrid.xyzroom import XYZRoom
from evennia.objects.objects import DefaultRoom
from world.overworld import Overworld, OverworldMap
from .objects import ObjectParent

CHAR_SYMBOL = "|w@|n"
CHAR_ALT_SYMBOL = "|w>|n"
ROOM_SYMBOL = "|bo|n"
LINK_COLOR = "|B"

_MAP_GRID = [
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", "@", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
]
_EXIT_GRID_SHIFT = {
    "north": (0, 1, "||"),
    "east": (1, 0, "-"),
    "south": (0, -1, "||"),
    "west": (-1, 0, "-"),
    "northeast": (1, 1, "/"),
    "southeast": (1, -1, "\\"),
    "southwest": (-1, -1, "/"),
    "northwest": (-1, 1, "\\"),
}


class Room(ObjectParent, DefaultRoom):
    """
    Simple room supporting game-specific mechanics.

    """

    allow_combat = False
    allow_pvp = False
    allow_death = False


class OverworldRoom(wilderness.WildernessRoom, Room):
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

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        return super().at_object_receive(source_location=source_location, moved_obj=moved_obj)


class TownRoom(Room, XYZRoom):
    """
    Combines the XYZGrid functionality with Ainneve-specific room code.
    """
    map_visual_range = 2


class PvPRoom(Room):
    """
    Room where PvP can happen, but noone gets killed.

    """

    allow_combat = True
    allow_pvp = True

    def get_display_footer(self, looker, **kwargs):
        """
        Display the room's PvP status.

        """
        return "|yNon-lethal PvP combat is allowed here!|n"