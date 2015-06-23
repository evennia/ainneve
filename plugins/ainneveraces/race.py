class Race(object):
    """
    Documentation
    """
    def __init__(self):
        self.name = ""
        self.size = ""
        self.slots = { 'head': None, 
                       'torso': None,
                       'arm_left': None,
                       'arm_right': None,
                       'leg_left': None,
                       'leg_right': None
                     }
        self.foci = []
        self.feats = []
        self.bonuses = {}
        self.detriments = {}
