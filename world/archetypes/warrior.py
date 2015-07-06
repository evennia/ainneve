import random

from world.archetypes.archetype import Archetype


class Warrior(Archetype):
    def __init__(self):
        super(Warrior, self).__init__()
        self.primary_traits.update({'strength': 6,
                                    'perception':5,
                                    'intelligence':4,
                                    'dexterity': 5,
                                    'charisma': 5,
                                    'vitality': 7,
                                    'magic': 4}
                                   )
        self.bonuses = {'power': 2}
        self.health_gain_on_level = random.randint(1, 6) + 2
