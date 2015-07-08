from evennia import DefaultObject

class BaseObject(DefaultObject):
    
    @property
    def short_desc(self):
        return self.key

    @short_desc.setter
    def short_desc(self, desc):
        self.key = "%s" % desc
        
    @property
    def long_desc(self):
        return self.db.desc
    
    @long_desc.setter
    def long_desc(self, desc):
        self.db.desc = "%s" % desc
