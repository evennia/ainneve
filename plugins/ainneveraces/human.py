from plugins.ainneveraces.race import Race


class Human(Race):
    def __init__(self):
        super(Human, self).__init__()
        self.name = "Human"
