class Archetype(object):
    def __init__(self):
        self.primary_traits = {'strength': 0,
                               'perception': 0,
                               'intelligence': 0,
                               'dexterity': 0,
                               'charisma': 0,
                               'vitality': 0,
                               'magic': 0}
        self.bonuses = {}

    @staticmethod
    def make_dual(a, b):
        dual_archetype =  Archetype()
        dual_archetype.primary_traits = \
            {k: (a.primary_traits[k] + b.primary_traits[k])/2
             for k in a.primary_traits.keys() + b.primary_traits.keys()}
        return dual_archetype
