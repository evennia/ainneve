class Archetype(object):
    def __init__(self):
        self.base = {
            'strength': 0,
            'perception': 0,
            'intelligence': 0,
            'dexterity': 0,
            'charisma': 0,
            'vitality': 0,
            'magic': 0,
            'movement': 0,
            'power': 0
        }
        self.health_die = None
        self.health_bonus = None

    @staticmethod
    def make_dual(a, b):
        duals = {
            frozenset(['Warrior', 'Scout']): 'Warrior-Scout',
            frozenset(['Warrior', 'Arcanist']): 'Warrior-Arcanist',
            frozenset(['Scout', 'Arcanist']): 'Arcanist-Scout'}
        dual = Archetype()
        dual.base = {k: (a.base[k] + b.base[k]) / 2
                     for k in a.base.keys() + b.base.keys()}
        dual.health_die = min(a.health_die, b.health_die)
        dual.health_bonus = min(a.health_bonus, b.health_bonus)
        dual.name = duals[frozenset([a.name, b.name])]
        dual.__class__.__name__ = dual.name.replace('-','')
        return dual
