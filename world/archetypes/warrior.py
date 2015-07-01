from world.archetypes.archetype import Archetype


class Warrior(Archetype):
    def __init__(self):
        super(Warrior, self).__init__()
        self.primary_traits.update({'strength': 6,
                                    'dexterity': 4,
                                    'charisma': 4,
                                    'vitality': 6}
                                   )

