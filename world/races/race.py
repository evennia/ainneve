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
            'left arm',
            'right arm',
            'left hand',
            'right hand',
            'left leg',
            'right leg',
            'left foot',
            'right foot'
        ]
        self.foci = []
        self.feats = []
        self.bonuses = {}
        self.detriments = {}
