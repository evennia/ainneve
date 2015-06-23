from plugins.ainneveraces.race import Race


class Human(Race):
    def __init__(self):
        super(Human, self).__init__()
        self.name = "Human"
        self.size = "medium"
        self.limbs = []
        self.slots = {}
        self.foci = ['agility', 'cunning', 'prestige']
        self.feats = ['sprint', 'improved jump', 'improved climb', 'improved swim', 'fear resistance']
        self.bonuses = {'will': 1, 'languages': 3}
        self.detriments = {}
