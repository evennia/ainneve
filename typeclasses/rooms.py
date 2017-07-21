# -*- encoding: utf-8 -*-

"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia.contrib.extended_room import ExtendedRoom
from evennia.contrib.rpsystem import ContribRPRoom

from utils.utils import get_directed_exits, EXIT_OFFSETS

def merge_terrains(base, child = {}):
    if isinstance(child, str):
        child = {'msg': child}
    result = base.copy()
    result.update(child)
    return result
mt = merge_terrains

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
    _EASY_TERRAIN = {'cost': 1, 'delay': 0}
    _MODERATE_TERRAIN = {'cost': 2, 'delay': 1}
    _DIFFICULT_TERRAIN = {'cost': 3, 'delay': 2}
    _EXTREME_TERRAIN = {'cost': 4, 'delay': 3}
    _TERRAINS = {
        # the strings here (without quotes) are acceptable parameters for @terrain
        'EASY': mt(_EASY_TERRAIN),
        'MODERATE': mt(_MODERATE_TERRAIN),
        'DIFFICULT': mt(_DIFFICULT_TERRAIN),
        'GRASS': mt(_EASY_TERRAIN),
        'ROAD': mt(_EASY_TERRAIN, {'cost': 0}),
        'MUD': mt(_DIFFICULT_TERRAIN, "You begin slogging {exit} through the mud. It is slow going."),
        'ICE': mt(_DIFFICULT_TERRAIN, "You carefully make your way {exit} over the icy path."),
        'QUICKSAND': {'cost': 5, 'delay': 4, 'msg': "Drawing on all your strength, you wade {exit} into the quicksand."},
        'SNOW': mt(_EXTREME_TERRAIN, "Your feet sinking with each step, you trudge {exit} into the snow."),
        'VEGETATION': mt(_MODERATE_TERRAIN, "You begin cutting your way {exit} through the thick vegetation."),
        'THICKET': mt(_MODERATE_TERRAIN, "You are greeted with the sting of bramble scratches as you make your way {exit} into the thicket."),
        'DEEPWATER': mt(_EXTREME_TERRAIN, {'cost': 3, 'msg': "You begin swimming {exit}."})
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

# https://stackoverflow.com/a/3221487/5244995
REVERSE_EXIT_OFFSETS = dict((v,k) for k,v in EXIT_OFFSETS.iteritems())
# TODO: diagonals (box-drawing only supports ╱, ╲, and ╳)
CENTERS = {
        'n': u'╷',
        'e': u'╶',
        's': u'╵',
        'w': u'╴',
      'e n': u'└',
      'n s': u'│',
      'n w': u'┘',
      'e s': u'┌',
      'e w': u'─',
      's w': u'┐',
    'e n w': u'┴',
    'e s w': u'┬',
    'n s w': u'┤',
    'e n s': u'├',
  'e n s w': u'┼'
}
SIDES = u'─'
class Road(Room):
    def at_object_creation(self):
        super(Room, self).at_object_creation()
        self.db.terrain = 'ROAD'

    def map_tile(self, _map, centers=CENTERS, sides=SIDES):
        directions = set()
        for room, delta in get_directed_exits(self).items():
            if isinstance(room, Road):
                direction = REVERSE_EXIT_OFFSETS.get(delta)
                if len(direction) == 1:
                    directions.add(direction)
        key = u' '.join(sorted(directions))
        left = sides if 'w' in directions else u' '
        right = sides if 'e' in directions else u' '
        return left + centers.get(key, '?') + right

BRIDGE_CENTERS = {
    # there’s no proper box drawing characters
    # for the plain directions
        'n': u'║',
        'e': u'═',
        's': u'║',
        'w': u'═',
      'e n': u'╚',
      'n s': u'║',
      'n w': u'╝',
      'e s': u'╔',
      'e w': u'═',
      's w': u'╗',
    'e n w': u'╩',
    'e s w': u'╦',
    'n s w': u'╣',
    'e n s': u'╠',
  'e n s w': u'╬'
}
BRIDGE_SIDES = u'═'
class Bridge(Road):
    def map_tile(self, _map, centers=BRIDGE_CENTERS, sides=BRIDGE_SIDES):
        return super(Bridge, self).map_tile(_map, centers, sides)
