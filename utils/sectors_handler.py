class SectorsHandler(object):
    """
    Handler for room's sectors
    """
    def __init__(self, obj):
        self.obj = obj
        self.sectors = (
                        'indoor',
                        'desert',
                        'urban',
                        'field',
                        'forest',
                        'hill',
                        'mountain',
                        'water',
                        'underwater',
                        'air'
                        )
    def set_sector(self, sector):
        if sector in self.sectors:
            self.obj.db.sector = sector
            string = "%s is now set as '%s'" % (self.obj.name, sector)
        else:
            string = "'%s' is not a valid sector type. Check 'help sectors' for a list." % sector
        return string
    
    def show(self):
        if self.obj.db.sector:
            return self.obj.db.sector
        else:
            return False
    
