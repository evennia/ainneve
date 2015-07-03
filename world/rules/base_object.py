"""
Base object typeclass. It defines some basic properties common to some base
typeclasses (Character, Room, Objects)
"""
from evennia import DefaultObject

class BaseObject(DefaultObject):
    def at_object_creation(self):
        self.db.short_desc = "%s" % self.name
        self.db.appearance = "You see {w%s{n" % self.name
        
    @property
    def short_desc(self):
        return self.db.short_desc
    
    @short_desc.setter
    def short_desc(self, *string):
        if string:
            self.db.short_desc = string
        else:
            self.db.short_desc = self.name
