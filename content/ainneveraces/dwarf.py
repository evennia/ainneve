from content.ainneveraces.race import Race


class Dwarf(Race):
    def __init__(self):
        super(Dwarf, self).__init__()
        self.name = "Dwarf"
        self.size = "small"
        self.foci = ['brawn', 'resilience', 'alertness']
        self.feats = [
            'heat vision', 'poison resistance', 'dark vision',
            'improved climb', 'fear resistance'
        ]
        self.bonuses = {'will': 1}
        self.detriments = {}
