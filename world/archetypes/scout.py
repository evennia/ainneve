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
        self.health_roll_on_level_up = (6)