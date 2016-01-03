"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.contrib.extended_room import *
from evennia import CmdSet


class Room(ExtendedRoom):
    """Base Ainneve Room typeclass.

    Properties:
        terrain (str): The terrain type for this room
        mv_cost (int): The movement cost to enter the room; based on
            `terrain` type
        range_field (tuple[int]): length and width of the room's combat
            range field
        max_chars (int): The maximum number of characters and mobs
            allowed to occupy the room. one char per square unit
    """
    # Define terrain constants
    _TERRAIN_COSTS = {
        'EASY': 1,
        'MODERATE': 2,
        'DIFFICULT': 3,
        'MUD': 3,
        'ICE': 3,
        'QUICKSAND': 5,
        'SNOW': 4,
        'VEGETATION': 2,
        'THICKET': 2,
        'DEEPWATER': 3,
    }

    def at_object_creation(self):
        super(Room, self).at_object_creation()
        self.db.terrain = 'EASY'
        self.db.range_field = (3, 3)
        self.db.errmsg_capacity = "There isn't enough room there for you."

    def at_object_receive(self,  moved_obj, source_location):
        if moved_obj.is_typeclass('typeclasses.characters.Character'):
            char_count = sum(
                1 for c in self.contents
                if c.is_typeclass('typeclasses.characters.Character'))

            if char_count + 1 > self.max_chars:
                # we're over capacity. send them back where they came
                moved_obj.msg(self.db.errmsg_capacity)
                moved_obj.move_to(source_location, quiet=True)

    # Terrain property, sets self.db.terrain_type, taken from the constats dict
    @property
    def terrain(self):
        return self.db.terrain
    
    @terrain.setter
    def terrain(self,value):
        if value in self._TERRAIN_COSTS:
            self.db.terrain = value
        else:
            raise ValueError('Invalid terrain type.')

    @property
    def mv_cost(self):
        """Returns the movement cost to enter this room."""
        return self._TERRAIN_COSTS[self.terrain]

    @property
    def range_field(self):
        """Returns a tuple representing the range field."""
        return self.db.range_field

    @range_field.setter
    def range_field(self, value):
        if (len(value) == 2
                and all(isinstance(v, int) and v > 0
                        for v in value)):
            self.db.range_field = tuple(value)
        else:
            raise ValueError('`range_field` must be a tuple of two positive integers.')

    # Maximum characters (mobs included) that can be in the room at the same time.
    @property
    def max_chars(self):
        """Return the maximum number of chars allowed in the room.

        Note:
            This value includes PCs, NPCs, and mobs.
        """
        return self.range_field[0] * self.range_field[1]


class ExtendedRoomCmdSet(CmdSet):
    """Command set containing ExtendedRoom commands."""
    def at_cmdset_creation(self):
        self.add(CmdExtendedLook())
        self.add(CmdExtendedDesc())
        self.add(CmdGameTime())
