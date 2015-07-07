import random

from world.archetypes.archetype import Archetype


class Arcanist(Archetype):
    def __init__(self):
        super(Arcanist, self).__init__()
        self.primary_traits.update({'perception': 4,
                                    'intelligence': 6,
                                    'charisma': 4,
                                    'magic': 6}
                                   )
        self.bonuses = {'power': 2, 'stamina': -2}
        self.movement = 7
        self.health_roll_on_level_up = (6, 1)
