class Archetype(object):
    """
    This class reprents the Archetype in Open Adventure for ainneve

    """
    def __init__(self, **kwargs):
        self.strength = None
        self.dexterity = None
        self.charisma = None
        self.vitality = None
        self.perception = None
        self.intelligence = None
        self.magic = None
        self.bonuses = {}
        self.mali = {}
        self.health_on_level_up = None
        
        # filling in the traits from the keyword args
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def getStats(self):
        return {'strength': self.strength,
                    'dexterity': self.dexterity,
                    'charisma': self.charisma,
                    'vitality': self.vitality,
                    'perception': self.perception,
                    'intelligence': self.intelligence,
                    'magic': self.magic,
                    'bonuses': self.bonuses,
                    'health_on_level_up': self.health_on_level_up}

    def setStats(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


    def getBonuses(self):
        return self.bonuses

    def setBonuses(self, **kwargs):
        for key, value in kwargs.items():
            self.bonuses.update({key: value})

    def getMali(self):
        return self._mali

    def setMali(self, **kwargs):
        for key, value in kwargs.items():
            self.mali.update({key: value})

    def getOn_Level_up(self):
        return self.health_on_level_up

    def setOn_Level_Up(self, value):
        # only records the amount of substracted or added health per 1d6
        # doesn't specify the type of dice
        if value in [int, float]:
            self.health_on_level_up = value
        else:
            return False

if __name__ == "__main__":
    arch_warrior = Archetype(strength=6, dexterity=4, charisma=4, vitality=6, bonuses={'power':2}, health_on_level_up=2)
    print(arch_warrior.getStats())