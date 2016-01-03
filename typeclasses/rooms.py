"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia.contrib.extended_room import ExtendedRoom


class Room(ExtendedRoom):
    """Base Ainneve Room typeclass.

    Properties:
        terrain (str): The terrain type for this room
        mv_cost (int): (read-only) The movement cost to enter the room; based on
            `terrain` type
        mv_delay (int): (read-only) The movement delay when entering the room;
            based on `terrain` type
        range_field (tuple[int]): length and width of the room's combat
            range field
        max_chars (int): The maximum number of characters and mobs
            allowed to occupy the room. one char per square unit
    """
    # Define terrain constants
    _TERRAINS = {
        'EASY': {'cost': 1, 'delay': 0},
        'MODERATE': {'cost': 2, 'delay': 1},
        'DIFFICULT': {'cost': 3, 'delay': 2},
        'MUD': {'cost':3, 'delay': 2, 'msg': "You begin slogging {exit} through the mud. It is slow going."},
        'ICE': {'cost': 3, 'delay': 2, 'msg': "You carefully make your way {exit} over the icy path."},
        'QUICKSAND': {'cost': 5, 'delay': 4, 'msg': "Drawing on all your stregnth, you wade {exit} into the quicksand."},
        'SNOW': {'cost': 4, 'delay': 3, 'msg': "Your feet sinking with each step, you trudge {exit} into the snow."},
        'VEGETATION': {'cost': 2, 'delay': 1, 'msg': "You begin cutting your way {exit} through the thick vegetation."},
        'THICKET': {'cost': 2, 'delay': 1, 'msg': "You are greeted with the sting of bramble scratches as you make your way {exit} into the thicket."},
        'DEEPWATER': {'cost': 3, 'delay': 3, 'msg': "You begin swimming {exit}."}
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
        if value in self._TERRAINS:
            self.db.terrain = value
            self.db.msg_start_move = self._TERRAINS[self.terrain].get('msg', None)
        else:
            raise ValueError('Invalid terrain type.')

    @property
    def mv_cost(self):
        """Returns the movement cost to enter this room."""
        return self._TERRAINS[self.terrain]['cost']

    @property
    def mv_delay(self):
        """Returns the movement delay for this room."""
        return self._TERRAINS[self.terrain]['delay']

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
