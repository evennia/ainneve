class Race(object):
    """
    Documentation
    """
    def __init__(self):
        self.name = ""
        self.size = ""
        self.slots = [
            'head',
            'torso',
            'left_arm',
            'right_arm',
            'left_leg',
            'right_leg'
        ]
        self.foci = []
        self.feats = []
        self.bonuses = {}
        self.detriments = {}
