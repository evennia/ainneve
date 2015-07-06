import random

from world.archetypes.archetype import Archetype


class Scout(Archetype):
    def __init__(self):
        super(Scout, self).__init__()
        self.primary_traits.update({
            'strength': 5,
            'perception': 6,
            'intelligence': 5,
            'dexterity': 7,
            'charisma': 5,
            'vitality': 5,
            'magic': 5
        })
        self.bonuses = {'reflex': 2}
        self.health_gain_on_level = random.randint(1, 6) + 2
