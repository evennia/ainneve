class Archetype(object):
    def __init__(self):
        self.template = {'strength': 0,
                         'perception': 0,
                         'intelligence': 0,
                         'dexterity': 0,
                         'charisma': 0,
                         'vitality': 0,
                         'magic': 0}
        self.health_die = None
        self.health_bonus = None

    @staticmethod
    def make_dual(a, b):
        dual =  Archetype()
        dual.template = \
            {k: (a.template[k] + b.template[k])/2
             for k in a.template.keys() + b.template.keys()}
        dual.health_die = min(a.health_die, b.health_die)
        dual.health_bonus = min(a.health_bonus, b.health_bonus)
        return dual
