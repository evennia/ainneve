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
    
    # Overloading default return_appearance method to show automatic exits
    # destinations and divide users and things. One user per line, one thing
    # per line. It's temporary: as object typeclass is ended, the method should
    # return the item short_desc or some "in_room_desc" (ex. A sword is dropped
    # here)
    
    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                                                    con.access(looker, "view"))
        exits, users, things = [], [], []
        for con in visible:
            if con.destination:
                exits.append("{w[%s] {n- {c%s{n" % (con.key, con.destination))
            elif con.has_player:
                users.append("{w%s{n is here." % con.short_desc)
            else:
                things.append("%s" % con.short_desc)
        # get description, build string
        string = "{c%s{n\n" % self.short_desc
        if self.long_desc:
            string += "%s" % self.long_desc
        if exits:
            string += "\n\n{rExits:\n{n" + "\n".join(exits)
        if users:
            string += "\n" + "".join(users)
        if things:
            string += "\n" + "\n".join(things)
        return string
    
    def basetype_setup(self):
        """
        Simple room setup setting locks to make sure the room
        cannot be picked up.

        """

        super(Room, self).basetype_setup()
        self.locks.add(";".join(["get:false()",
                                 "puppet:false()"])) # would be weird to puppet a room ...
        self.location = None


class ChargenRoom(DefaultRoom):
    """Room typeclass for character generation process."""
    def at_object_creation(self):
        self.cmdset.add_default(ChargenCmdSet, permanent=True)
