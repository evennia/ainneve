import random

from world.archetypes import Archetype


class Arcanist(Archetype):
    def __init__(self):
        super(Arcanist, self).__init__()
        self.name = 'Arcanist'
        self.base.update({
            'perception': 4,
            'intelligence': 6,
            'charisma': 4,
            'magic': 6,
            'movement': 7,
            'power': 2,
            'stamina': -2
         })
        self.health_die = 6
        self.health_bonus = -1
