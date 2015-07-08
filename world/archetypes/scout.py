import random

from world.archetypes.archetype import Archetype


class Scout(Archetype):
    def __init__(self):
        super(Scout, self).__init__()
        self.template.update({'strength': 4,
                              'dexterity': 4,
                              'perception': 6,
                              'intelligence': 6,
                              'movement': 7}
                             )
        self.health_die = 6
        self.health_bonus = 0