import random

from world.archetypes.archetype import Archetype


class Arcanist(Archetype):
    def __init__(self):
        super(Arcanist, self).__init__()
        self.primary_traits.update({
            'strength': 4,
            'perception': 5,
            'intelligence': 7,
            'dexterity': 5,
            'charisma': 5,
            'vitality': 5,
            'magic': 6
        })
        self.bonuses = {'mana': 2}
        self.health_gain_on_level = random.randint(1, 6) + 1
