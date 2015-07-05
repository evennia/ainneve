class Group(object):
    FRONT_LEFT = 0
    FRONT_CENTER = 1
    FRONT_RIGHT = 2
    BACK_LEFT = 3
    BACK_CENTER = 4
    BACK_RIGHT = 5

    def __init__(self):
        self.name = ''
        self.leader = None
        self.members = []
        self.positions = {}

    def toggle_row(self, member):
        pass

    def change_columb(self, member, column):
        pass
