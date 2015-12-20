"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia import DefaultRoom
from commands.chargen import ChargenCmdSet
from typeclasses.characters import Character
from objects import Object

class Room(Object):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    # Define terrain constants
    TERRAIN_TYPES = {
                    'INDOOR':0,
                    'URBAN':1,
                    'FIELD':2,
                    'FOREST':3,
                    'DESERT':4,
                    'MOUNTAIN':5,
                    'WATER':6,
                    'UNDERWATER':7,
                    'FLYING':8
                    }
    
    # Terrain property, sets self.db.terrain_type, taken from the constats dict
    @property
    def terrain(self):
        return self.db.terrain
    
    @terrain.setter
    def terrain(self,value):
        if value in self.TERRAIN_TYPES:
            self.db.terrain = self.TERRAIN_TYPES[value]
        else:
            raise ValueError('This terrain type does not exist.')
    
    # Maximum characters (mobs included) that can be in the room at the same time.
    @property
    def max_chars(self):
        return self.db.max_chars
    
    @max_chars.setter
    def max_chars(self, value):
        if type(value) is not int:
            raise TypeError('Number of maximum characters has to be an integer.')
        else:
            self.db.max_chars = value

    def basetype_setup(self):
        """
        Simple room setup setting locks to make sure the room
        cannot be picked up.

        """

        super(Room, self).basetype_setup()
        self.locks.add(";".join(["get:false()",
                                 "puppet:false()"])) # would be weird to puppet a room ...
        self.location = None

