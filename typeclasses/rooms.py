"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia.contrib.extended_room import ExtendedRoom
from evennia.contrib.rpsystem import ContribRPRoom


class Room(ExtendedRoom, ContribRPRoom):
    """Base Ainneve Room typeclass.

    Properties:
        terrain (str): The terrain type for this room
        mv_cost (int): (read-only) The movement cost to enter the room; based on
            `terrain` type
        mv_delay (int): (read-only) The movement delay when entering the room;
            based on `terrain` type
        max_chars (int): The maximum number of characters and mobs
            allowed to occupy the room. one char per square unit
    """
    # Define terrain constants
    _TERRAINS = {
        'EASY': {'cost': 1, 'delay': 0},
        'MODERATE': {'cost': 2, 'delay': 1},
        'DIFFICULT': {'cost': 3, 'delay': 2},
        'MUD': {'cost': 3, 'delay': 2, 'msg': "You begin slogging {exit} through the mud. It is slow going."},
        'ICE': {'cost': 3, 'delay': 2, 'msg': "You carefully make your way {exit} over the icy path."},
        'QUICKSAND': {'cost': 5, 'delay': 4, 'msg': "Drawing on all your strength, you wade {exit} into the quicksand."},
        'SNOW': {'cost': 4, 'delay': 3, 'msg': "Your feet sinking with each step, you trudge {exit} into the snow."},
        'VEGETATION': {'cost': 2, 'delay': 1, 'msg': "You begin cutting your way {exit} through the thick vegetation."},
        'THICKET': {'cost': 2, 'delay': 1, 'msg': "You are greeted with the sting of bramble scratches as you make your way {exit} into the thicket."},
        'DEEPWATER': {'cost': 3, 'delay': 3, 'msg': "You begin swimming {exit}."}
    }

    def at_object_creation(self):
        super(Room, self).at_object_creation()
        self.db.terrain = 'EASY'
        self.db.max_chars = 0
        self.db.errmsg_capacity = "There isn't enough room there for you."

    def at_object_receive(self,  moved_obj, source_location):
        if moved_obj.is_typeclass('typeclasses.characters.Character'):
            char_count = sum(
                1 for c in self.contents
                if c.is_typeclass('typeclasses.characters.Character'))

            if self.db.max_chars > 0 and char_count + 1 > self.db.max_chars:
                # we're over capacity. send them back where they came
                moved_obj.msg(self.db.errmsg_capacity)
                moved_obj.move_to(source_location, quiet=True)

    # Terrain property, sets self.db.terrain_type, taken from the constants dict
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


