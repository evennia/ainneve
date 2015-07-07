class FlagsHandler(object):
    """
    An handler to manage flags
    """

    def __init__(self, obj):
        #save parent typeclass
        self.obj = obj

    def add(self, flag):
        self.obj.tags.add(flag, category='flags')

    def remove(self, flag):
        if self.obj.tags.get(flag, category='flags'):
            self.obj.tags.remove(flag, category='flags')
    def lists(self):
        tagtuples = self.obj.tags.all(return_key_and_category=True)
        ntags = len(tagtuples)
        tags = [tup[0] for tup in tagtuples]
        categories = [" (category: %s)" % tup[1] if tup[1] else "" for tup in tagtuples]
        if ntags:
            string = "Tag%s on %s: %s" % ("s" if ntags > 1 else "", self.obj, ", ".join("'%s'%s" % (tags[i], categories[i]) for i in range(ntags)))
        else:
            string = "No tags attached to %s." % self.obj
        return string

    def check(self, flag, default=False):
        if self.obj.tags.get(flag, category='flags'):
            if hasattr(self.obj, flag):
                return getattr(self.obj, flag)
            return True
        return default
