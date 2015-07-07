class FlagsHandler(object):
    """
    An handler to manage flags
    """

    def __init__(self, obj):
        #save parent typeclass
        self.obj = obj
        # load flag tuple
        self.flags = (
                "is_indoor",
                "is_dark",
                "is_safe",
                "has_road",
                "no_magic",
                "no_teleport",
                "no_summon",
                "is_silent",
                "no_range",
                "is_water",
                "is_air",
                "no_quit"
                )

    def add(self, flag):
        if flag in self.flags:
            self.obj.tags.add(flag, category='flags')
            string = "Added '%s' flag on '%s'" % (flag, self.obj)
            return string
        else:
            string = "%s is not a valid flag. Check help @flag for instructions." % flag
            return string

    def remove(self, flag):
        if self.obj.tags.get(flag, category='flags'):
            self.obj.tags.remove(flag, category='flags')
            string = "'%s' flag was removed from '%s'" % (flag, self.obj)
            return string
        else:
            string = "'%s' flag is not present on '%s'" % (flag, self.obj)
            return string
            
    def lists(self):
        tagtuples = self.obj.tags.all(return_key_and_category=True)
        flagstuple = [tag[0] for tag in tagtuples if tag[1] == "flags"]
        ntags = len(flagstuple)
        if ntags:
            string = "Flag%s on %s: %s" % ("s" if ntags > 1 else "", self.obj, ", ".join("'%s'" % flagstuple[i] for i in range(ntags)))
        else:
            string = "No tags attached to %s." % self.obj
        return string

    def check(self, flag, default=False):
        if self.obj.tags.get(flag, category='flags'):
            if hasattr(self.obj, flag):
                return getattr(self.obj, flag)
            return True
        return default
