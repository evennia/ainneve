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
        self.level_up_health_die = 6
        self.level_up_health_bonus = -1
