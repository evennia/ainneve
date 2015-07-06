class Archetype(object):
    def __init__(self):
        self.primary_traits = {
          'strength': 0,
          'perception': 0,
          'intelligence': 0,
          'dexterity': 0,
          'charisma': 0,
          'vitality': 0,
          'magic': 0
        }
        self.bonuses = {}
        self.health_gain_on_level = None
