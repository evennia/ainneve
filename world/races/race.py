class Race(object):
    """
    Documentation
    """
    def __init__(self):
        self.name = ""
        self.size = ""
        self.slots = [
            'armor',
            'wield1',
            'wield2',
        ]

        #self.limbs = {
        #    'head':         ('head', 'left ear', 'right ear', 'on eyes',
        #                     'neck1', 'neck2',),
        #    'torso':        ('torso', 'shoulders', 'back', 'belt1', 'belt2',),
        #    'left arm':     ('arms', 'left wrist',),
        #    'right arm':    ('arms', 'right wrist',),
        #    'left hand':    ('hands', 'left finger', 'wield2',),
        #    'right hand':   ('hands', 'right finger', 'wield1',),
        #    'left leg':     ('legs',),
        #    'right leg':    ('legs',),
        #    'left foot':    ('feet',),
        #    'right foot':   ('feet',),
        #}

        self.foci = []
        self.feats = []
        self.bonuses = {}
        self.detriments = {}
