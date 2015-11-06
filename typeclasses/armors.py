"""
Armor typeclasses
"""

from typeclasses.items import Item

class Armor(Item):
    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.toughness = 0
        self.db.abilities = []
        self.db.slot = []
        self.db.slot_operator = 'AND'


# typeclasses for prototyping


class Headwear(Armor):
    """Typeclass for armor prototypes worn on the head."""
    def at_object_creation(self):
        super(Headwear, self).at_object_creation()
        self.db.slot = ['head']


class Shoulderwear(Armor):
    """Typeclass for armor prototypes worn on the shoulders."""
    def at_object_creation(self):
        super(Shoulderwear, self).at_object_creation()
        self.db.slot = ['shoulders']


class Breastplate(Armor):
    """Typeclass for sleeveless armor prototypes."""
    def at_object_creation(self):
        super(Breastplate, self).at_object_creation()
        self.db.slot = ['torso']


class SleevedShirt(Breastplate):
    """Typeclass for full upper body armor prototypes."""
    def at_object_creation(self):
        super(SleevedShirt, self).at_object_creation()
        self.db.slot += ['arms']


class Armband(Armor):
    """Typeclass for arm band prototypes."""
    def at_object_creation(self):
        super(Armband, self).at_object_creation()
        self.db.slot = ['left wrist', 'right wrist']
        self.db.slot_operator = 'OR'


class Gloves(Armor):
    """Typeclass for armor prototypes for the hands."""
    def at_object_creation(self):
        super(Gloves, self).at_object_creation()
        self.db.slot = ['hands']


class Gauntlets(Gloves):
    """Typeclass for long glove armor prototypes."""
    def at_object_creation(self):
        super(Gauntlets, self).at_object_creation()
        self.db.slot += ['left wrist', 'right wrist']


class Belt(Armor):
    """Typeclass for armor prototypes worn in belt slots."""
    def at_object_creation(self):
        super(Belt, self).at_object_creation()
        self.db.slot = ['belt1', 'belt2']
        self.db.slot_operator = 'OR'


class Legwear(Armor):
    """Typeclass for armor prototypes worn on the legs."""
    def at_object_creation(self):
        super(Legwear, self).at_object_creation()
        self.db.slot = ['legs']


class Footwear(Armor):
    """Typeclass for armor prototypes worn on the feet."""
    def at_object_creation(self):
        super(Footwear, self).at_object_creation()
        self.db.slot = ['feet']


class Shroud(Armor):
    """Typeclass for arcanist shroud prototypes."""
    def at_object_creation(self):
        super(Shroud, self).at_object_creation()
        self.db.slot = ['torso', 'arms', 'left wrist', 'right wrist', 'legs']

