import random

from world.archetypes.archetype import Archetype


class Warrior(Archetype):
    def __init__(self):
        super(Warrior, self).__init__()
        self.primary_traits.update({'strength': 6,
                                    'dexterity': 4,
                                    'charisma': 4,
                                    'vitality': 6}
                                   )
        self.bonuses = {'power': 2}
        self.movement = 5
        self.level_up_health_die = 6
        self.level_up_health_bonus = 1
