import random

from world.archetypes.archetype import Archetype


class Scout(Archetype):
    def __init__(self):
        super(Scout, self).__init__()
        self.primary_traits.update({'strength': 4,
                                    'dexterity': 4,
                                    'perception': 6,
                                    'intelligence': 6}
                                   )
        self.movement = 7
        self.level_up_health_die = 6
        self.level_up_health_bonus = 0