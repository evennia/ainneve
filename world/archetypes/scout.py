import random

from world.archetypes import Archetype


class Scout(Archetype):
    def __init__(self):
        super(Scout, self).__init__()
        self.name = 'Scout'
        self.base.update({'strength': 4,
                              'dexterity': 4,
                              'perception': 6,
                              'intelligence': 6,
                              'movement': 7}
                             )
        self.health_die = 6
        self.health_bonus = 0