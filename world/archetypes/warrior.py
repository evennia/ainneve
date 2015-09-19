import random

from world.archetypes import Archetype


class Warrior(Archetype):
    def __init__(self):
        super(Warrior, self).__init__()
        self.name = 'Warrior'
        self.base.update({
            'strength': 6,
            'dexterity': 4,
            'charisma': 4,
            'vitality': 6,
            'movement': 5,
            'power': 2
        })
        self.health_die = 6
        self.health_bonus = 1
