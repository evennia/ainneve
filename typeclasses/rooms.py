"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    
    
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
                users.append("{w%s{n is here." % key)
            else:
                things.append("%s" % key)
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
