"""
Prototype module containing weapons and shields.
"""

from evennia.utils.evtable import fill

## Generic weapons

HUNTING_KNIFE = \
    {"key": "a hunting knife",
     "aliases": ["knife"],
     "typeclass": "typeclasses.weapons.Weapon",
     "desc": "A trusty blade used by survivalists throughout Ainneve. " +
             "Its well-worn maple handle holds a tarnished but sharp blade.",
     "weight": 0.5,
     "value": 15,
     "damage": 1}


## Warrior Weapons

IRON_HAND_AXE = \
    {"key": "an iron hand axe",
     "aliases": ["hand axe", "axe"],
     "typeclass": "typeclasses.weapons.Weapon",
     "desc": "This axe has a tarnished blade which appears to have been " +
             "separated and re-attached at some point, but it seems to " +
             "be holding together for now.",
     "weight": 1,
     "value": 50,
     "damage": 2}

IRON_THROWING_AXE = \
    {"key": "an iron throwing axe",
     "aliases": ["throwing axe", "axe"],
     "typeclass": "typeclasses.weapons.RangedWeapon",
     "desc": "This axe is fairly well-balanced but heavy due to its iron " +
             "construction.",
     "weight": 2,
     "value": 80,
     "damage": 0}

IRON_LONGSWORD = \
    {"key": "an iron longsword",
     "aliases": ["longsword"],
     "typeclass": "typeclasses.weapons.Weapon",
     "desc": "Blood stains and dirt smudge the iron blade of this " +
             "longsword. Surely it has seen its share of battle.",
     "weight": 2,
     "value": 400,
     "damage": 3}

IRON_MAUL = \
    {"key": "a large iron maul",
     "aliases": ["maul"],
     "typeclass": "typeclasses.weapons.TwoHandedWeapon",
     "desc": "A heavy mass of metal mounted atop a sturdy staff. " +
             "It can deliver crushing blows, if you have the stamina " +
             "to wield it.",
     "weight": 5,
     "value": 200,
     "damage": 4}


## Scout Weapons

LEATHER_WHIP = \
    {"key": "a leather whip",
     "aliases": ["whip"],
     "typeclass": "typeclasses.weapons.Weapon",
     "desc": "Sixteen strands of leather, braided tightly in multiple " +
             "layers. It extends the user's reach and can be used to disarm.",
     "weight": 1,
     "value": 30,
     "damage": 1}

IRON_RAPIER = \
    {"key": "an iron rapier",
     "aliases": ["rapier"],
     "typeclass": "typeclasses.weapons.Weapon",
     "desc": "Mottled by age and oxidation, this rapier's blade has seen " +
             "better days, but the hilt has been rebuilt and looks new.",
     "weight": 1,
     "value": 300,
     "damage": 3}

MAPLE_SHORT_BOW = \
    {"key": "a maple short bow",
     "aliases": ["bow"],
     "typeclass": "typeclasses.weapons.TwoHandedRanged",
     "desc": "This bow has a rich patina from years of use, but its draw is " +
             "firm and it will still accurately deliver an arrow to the heart " +
             "of your enemies.",
     "weight": 1,
     "value": 30,
     "damage": 0,
     "range": 10}

LEATHER_BUCKLER = \
    {"key": "a leather buckler",
     "aliases": ["buckler"],
     "typeclass": "typeclasses.armors.Shield",
     "desc": "Small, round, and made of stiffened laminated leather, this " +
             "light hand shield is simple and functional in its design.",
     "weight": 2,
     "value": 100,
     "toughness": 1}

## Arcanist weapons

MAPLE_STAFF = \
    {"key": "a super magical staff",
     "aliases": ["staff"],
     "typeclass": "typeclasses.items.Equippable",
     "desc": "This staff is more of a placeholder than anything, as the " +
             "magic system doesn't exist yet.",
     "weight": 2,
     "value": 2,
     "slot": ["wield1", "wield2"],
     "slot_operator": "AND"}

# format all `desc` properties consistently
for proto in globals().values():
    if isinstance(proto, dict) and 'desc' in proto:
        proto['desc'] = fill(proto['desc'])

