"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from utils.flags_handler import FlagsHandler
from utils.sectors_handler import SectorsHandler

class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    
    # Sectors handled by sectors handler
    @property
    def sector(self):
        return SectorsHandler(self)
    
    # Flags handled by Nadorrano's handler
    @property
    def flags(self):
        return FlagsHandler(self)
    
    # Room size. This will affect combat in some way at some point.
    @property
    def room_size(self):
        return self.db.room_size
        
    @room_size.setter
    def room_size(self, value):
        if value is "small":
            self.db.room_size = 0
        elif value is "medium":
            self.db.room_size = 1
        elif value is "large":
            self.db.room_size = 2
        else:
            raise ValueError('The room size need to match standard string. Check help @size for further instructions.')
    
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
    
    # Return movement points needed to traverse.
    @property
    def move_request(self):
        return self.db.move_request
        
    @move_request.setter
    def move_request(self, value):
        if type(value) is not int:
            raise TypeError('Movement points value needs to be an integer.')
        else:
            self.db.move_request = value
    
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
            key = con.key
            if con.destination:
                exits.append("{w[%s] {n- {c%s{n" % (key, con.destination))
            elif con.has_player:
                users.append("{w%s{n is here." % con.key)
            else:
                things.append("%s" % con.key)
        # get description, build string
        string = "{c%s{n\n" % self.key
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if exits:
            string += "\n\n{rExits:\n{n" + "\n".join(exits)
        if users:
            string += "\n" + "".join(users)
        if things:
            string += "\n" + "\n".join(things)
        return string
        
#class Urban(Room):
#    """
#    This class is the default urban location. Anything going from a city square
#    to a village road should be built upon this class.
#    """
#    
#    # Adding default flags as tag. The flags must be created under category "flag"
#    def at_object_creation(self):
#        self.tags.add("has_road", category="flags")
#        self.max_chars = 20
#        self.move_request = 1
