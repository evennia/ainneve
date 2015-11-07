"""
Armor typeclasses
"""

from typeclasses.items import Equippable, Item

class Armor(Item, Equippable):
    """
    Typeclass for armor objects.
    """

    # primary defensive stat
    toughness = 0

    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.toughness = self.toughness


# typeclasses for prototyping


class Headwear(Armor):
    """Typeclass for armor prototypes worn on the head."""
    slots = ['head']


class Shoulderwear(Armor):
    """Typeclass for armor prototypes worn on the shoulders."""
    slots = ['shoulders']


class Breastplate(Armor):
    """Typeclass for sleeveless armor prototypes."""
    slots = ['torso']


class UnderShirt():
    """Typeclass for shirts worn beneath Breastplates."""
    slots = ['arms']


class SleevedShirt(Armor):
    """Typeclass for full upper body armor prototypes."""
    slots = ['torso', 'arms']


class Armband(Armor):
    """Typeclass for arm band/bracelet prototypes."""
    slots = ['left wrist', 'right wrist']
    slot_operator = 'OR'


class Gloves(Armor):
    """Typeclass for armor prototypes for the hands."""
    slots = ['hands']


class Gauntlets(Gloves):
    """Typeclass for long glove armor prototypes."""
    slots = ['hands', 'left wrist', 'right wrist']
    slot_operator = 'AND'


class Belt(Armor):
    """Typeclass for armor prototypes worn in belt slots."""
    slots = ['belt1', 'belt2']
    slot_operator = 'OR'


class Legwear(Armor):
    """Typeclass for armor prototypes worn on the legs."""
    slots = ['legs']


class Footwear(Armor):
    """Typeclass for armor prototypes worn on the feet."""
    slots = ['feet']


class Shroud(Armor):
    """Typeclass for arcanist shroud prototypes."""
    slots = ['torso', 'arms', 'legs']
    slot_operator = 'AND'

