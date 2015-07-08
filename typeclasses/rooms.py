"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from utils.flags_handler import FlagsHandler
from utils.sectors_handler import SectorsHandler
from baseobject import BaseObject

class Room(BaseObject, DefaultRoom):
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
