"""
Prototype module containing armor.
"""

from evennia.utils import fill
from world.economy import SC, CC

# Armor

CLOTH_GARMENT = {
    "key": "a cloth garment",
    "aliases": ["cloth garment", "cl garment", "cloth", "garment"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "Made of soft cloth, this garment provides minimal protection.",
    "weight": 2,
    "value": 50*CC,
    "toughness": 0,
}

LEATHER_GARMENT = {
    "key": "a leather garment",
    "aliases": ["leather garment", "le garment", "leather", "garment"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "This leather garment has stiffened panels on all sides for "
            "protection, but its joints are well-tailored and won't "
            "inhibit movement.",
    "weight": 1,
    "value": 1*SC,
    "toughness": 1,
}

BRIGANDINE = {
    "key": "a brigandine",
    "aliases": ["brigandine"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "Layers of stiffened leather have been laminated together for "
            "the breastplate of this simple brigandine.",
    "weight": 10,
    "value": 3*SC,
    "toughness": 2,
}

CHAIN_MAIL = {
    "key": "chain mail",
    "typeclass": "typeclasses.armors.Armor",
    "desc": "The fine mesh of this chain mail suit is highly resistant to "
            "slicing damage.",
    "weight": 18,
    "value": 5*SC,
    "toughness": 2,
}

PLATED_MAIL = {
    "key": "plated mail",
    "aliases": ["plate", "plate mail", "pl mail", "mail"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "This armor has an underlayer of chain mail, reinforced with "
            "metal plating in the arms, shoulders, and torso.",
    "weight": 18,
    "value": 15*SC,
    "toughness": 3,
}

IRON_SCALE = {
    "key": "iron scale mail",
    "aliases": ["iron", "scale", "mail", "scale mail", "iron scale", "iron armor"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "Plated with an offset pattern of squared off iron 'scales,' "
            "this heavy suit of armor offers good protection",
    "weight": 14,
    "value": 20*SC,
    "toughness": 5,
}

IRON_BANDED = {
    "key": "iron banded armor",
    "aliases": ["iron banded", "iron armor", "iron", "banded", "armor",
                "banded armor"],
    "typeclass": "typeclasses.armors.Armor",
    "desc": "This suit of armor is comprised of a series of overlapping "
            "horizontal bands of iron that provide great protection but "
            "still allow free movement.",
    "weight": 15,
    "value": 25*SC,
    "toughness": 7,
}

# Shields

BUCKLER_SHIELD = {
    "key": "a buckler",
    "aliases": ["buckler"],
    "typeclass": "typeclasses.armors.Shield",
    "desc": "Small, round, and made of stiffened laminated leather, this "
            "light hand shield is simple and functional in its design.",
    "weight": 2,
    "value": 1*SC,
    "toughness": 1,
}

HERALDIC_SHIELD = {
    "key": "a heraldic shield",
    "aliases": ["heraldic shield", "he shield", "heraldic", "shield"],
    "typeclass": "typeclasses.armors.Shield",
    "desc": "This medium shield is faced with metal to better deflect "
            "incoming blows.",
    "weight": 6,
    "value": 2*SC,
    "toughness": 2,
}

TOWER_SHIELD = {
    "key": "a tower shield",
    "aliases": ["tower shield", "tower", "shield", "to shield"],
    "typeclass": "typeclasses.armors.Shield",
    "desc": "Large and made of dense materials, you could hide "
            "your entire body behind this shield, but don't try "
            "to run with it.",
    "weight": 13,
    "value": 3*SC,
    "toughness": 3,
}
