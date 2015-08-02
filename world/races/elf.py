from world.races import Race


class Elf(Race):
    def __init__(self):
        super(Elf, self).__init__()
        self.name = "Elf"
        self.size = "medium"
        self.foci = ['agility', 'spirit', 'alertness']
        self.feats = [
            'magic resistance', 'heat vision', 'improved listen', 'sprint',
            'illusion resistance'
        ]
        self.bonuses = {}
        self.detriments = {}
