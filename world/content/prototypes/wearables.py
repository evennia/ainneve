"""
Prototype module containing clothing and armor.
"""

from evennia.utils.evtable import fill

## Generic starter clothing

STARTER_SHIRT = \
    {"key": "a linen tunic",
     "aliases": ["tunic", "shirt"],
     "typeclass": "typeclasses.armors.SleevedShirt",
     "desc": "Made of rough linen, this shirt's only value is its utility. " +
             "Off-white and poorly fitting, it is otherwise unremarkable.",
     "weight": 1,
     "value": 20,
     "toughness": 0}

STARTER_PANTS = \
    {"key": "linen pants",
     "aliases": ["pants"],
     "typeclass": "typeclasses.armors.Legwear",
     "desc": "These homespun pants are light and comfortable, " +
             "but provide little to no protection.",
     "weight": 2,
     "value": 25,
     "toughness": 0}

STARTER_SHOES = \
    {"key": "homespun shoes",
     "aliases": ["shoes"],
     "typeclass": "typeclasses.armors.Footwear",
     "desc": "The woven soles of these shoes are soft and provide little " +
             "protection against rocky ground.",
     "weight": 0.5,
     "value": 10,
     "toughness": 0}

STARTER_HAT = \
    {"key": "a straw hat",
     "aliases": ["hat"],
     "typeclass": "typeclasses.armors.Headwear",
     "desc": "Made of reeds grown on the Plains of Man and woven together, " +
             "this hat provides protection from the sun. It's so light " +
             "that the wind might well take it away.",
     "weight": 0.5,
     "value": 5,
     "toughness": 0}


##  Warrior Armor

STARTER_WAR_BRIGANDINE = \
    {"key": "a leather brigandine",
     "aliases": ["brigandine", "breastplate"],
     "typeclass": "typeclasses.armors.Breastplate",
     "desc": "Layers of stiffened leather have been laminated together for " +
             "the breastplate of this simple brigandine.",
     "weight": 10,
     "value": 300,
     "toughness": 2}

STARTER_WAR_GREAVES = \
    {"key": "leather greaves",
     "aliases": ["greaves", "pants"],
     "typeclass": "typeclasses.armors.Legwear",
     "desc": "These protective leg coverings have a supple leather lining " +
             "and are reinforced with laminated leather and padding.",
     "weight": 12,
     "value": 175,
     "toughness": 1}

STARTER_WAR_BOOTS = \
    {"key": "leather boots",
     "aliases": ["boots"],
     "typeclass": "typeclasses.armors.Footwear",
     "desc": "These sturdy boots rise to mid-calf, and has laces up the " +
             "front that conceal a laminated leather shin guard.",
     "weight": 5,
     "value": 150,
     "toughness": 1}

STARTER_WAR_HELM = \
    {"key": "leather helm",
     "aliases": ["helm"],
     "typeclass": "typeclasses.armors.Headwear",
     "desc": "Made of stiff, reinforced leather, this helmet  protects " +
             "the head and neck without compromising field of vision.",
     "weight": 2,
     "value": 75,
     "toughness": 0.5}

STARTER_WAR_GAUNTLETS = \
    {"key": "leather gauntlets",
     "aliases": ["gauntlets"],
     "typeclass": "typeclasses.armors.Gauntlets",
     "desc": "These are long, reinforced leather gloves that cover the " +
             "hands and forearms",
     "weight": 1,
     "value": 50,
     "toughness": 0.5}


## Scout Armor

STARTER_SCO_RAGLAN = \
    {"key": "a leather raglan",
     "aliases": ["raglan", "shirt"],
     "typeclass": "typeclasses.armors.SleevedShirt",
     "desc": "This leather shirt has stiffened panels on all sides for " +
             "protection, but its joints are well-tailored and won't " +
             "inhibit movement. ",
     "weight": 4,
     "value": 100,
     "toughness": 1}

STARTER_SCO_LEGGINGS = \
    {"key": "leather leggings",
     "aliases": ["leggings", "pants"],
     "typeclass": "typeclasses.armors.Legwear",
     "desc": "These sleek leather pants have a sleek fit. Dark and matte " +
             "in color, the wearer could easily slip into the shadows.",
     "weight": 5,
     "value": 100,
     "toughness": 1}

STARTER_SCO_SHOES = \
    {"key": "leather shoes",
     "aliases": ["shoes"],
     "typeclass": "typeclasses.armors.Footwear",
     "desc": "With a medium sole and rising low on the ankles, these shoes " +
             "make for light stepping",
     "weight": 2,
     "value": 50,
     "toughness": 0}

STARTER_SCO_CAPE = \
    {"key": "a dark cape",
     "aliases": ["cape"],
     "typeclass": "typeclasses.armors.Shoulderwear",
     "desc": "Made of flowing fabric, this cape can be used both to slink " +
             "away stealthily and to protect yourself in battle.",
     "weight": 3,
     "value": 40,
     "toughness": 1}

STARTER_SCO_GLOVES = \
    {"key": "soft leather gloves",
     "aliases": ["gloves"],
     "typeclass": "typeclasses.armors.Gloves",
     "desc": "Smooth and shiny, these gloves look as though they haven't " +
             "seen a day of adventuring.",
     "weight": 1,
     "value": 30,
     "toughness": 0}


## Arcanist Vestments

STARTER_ARC_SHROUD = \
    {"key": "a novice shroud",
     "aliases": ["shroud", "robes"],
     "typeclass": "typeclasses.armors.Shroud",
     "desc": "The soft grey cotton of this shroud has been infused with " +
             "magical energy and pulses with potentialities almost " +
             "imperceptibly.",
     "weight": 4,
     "value": 50,
     "toughness": 0}

STARTER_ARC_BELT = \
    {"key": "a novice crystal lanyard",
     "aliases": ["lanyard", "crystal", "crystal lanyard"],
     "typeclass": "typeclasses.armors.Belt",
     "desc": "A cluster of crystals dangle from the clasp of the lanyard's " +
             "soft cord, helping the novice to better focus magical " +
             "energies.",
     "weight": 1,
     "value": 50,
     "toughness": 0}

STARTER_ARC_FOOTWRAPS = \
    {"key": "novice footwraps",
     "aliases": ["footwraps", "shoes"],
     "typeclass": "typeclasses.armors.Footwear",
     "desc": "Novice Arcanists wear these scant foot coverings to help " +
             "them learn to more effectively draw magical energy from " +
             "the environment around them.",
     "weight": 1,
     "value": 50,
     "toughness": 0}

STARTER_ARC_HEADBAND = \
    {"key": "a novice headband",
     "aliases": ["headband"],
     "typeclass": "typeclasses.armors.Headwear",
     "desc": "Embroidered with a symbol of arcane wisdom, this headband " +
             "helps a novice Arcanist to commune with magical knowledge.",
     "weight": 0.5,
     "value": 50,
     "toughness": 0}

STARTER_ARC_WRISTBAND = \
    {"key": "novice wristband",
     "aliases": ["wristband"],
     "typeclass": "typeclasses.armors.Armband",
     "desc": "A leather wrist wrap with a dark metal inlay in the center. ",
     "weight": 0.5,
     "value": 40,
     "toughness": 0}

# format all `desc` properties consistently
for proto in globals().values():
    if isinstance(proto, dict) and 'desc' in proto:
        proto['desc'] = fill(proto['desc'])

