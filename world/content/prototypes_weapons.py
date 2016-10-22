"""
Prototype module containing weapons and shields.
"""

from evennia.utils import fill
from world.economy import SC, CC

## Weapons from OA

HAND_AXE = {
    "key": "a hand axe",
    "aliases": ["hand axe", "axe"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "The blade of this axe appears well-used and slightly "
            "tarnished, but its handle is straight and sturdy.",
    "weight": 1,
    "value": 60*CC,
    "damage": 2,
    "range": "melee"
}

BATTLE_AXE = {
    "key": "a battle axe",
    "aliases": ["battle axe", "axe"],
    "typeclass": "typeclasses.weapons.TwoHandedWeapon",
    "desc": "Sturdy and with significant heft, this axe has a menacingly "
            "large blade, and a hard swing of it can send enemies flying. ",
    "weight": 3,
    "value": 3*SC,
    "damage": 4,
    "range": "melee"
}

DAGGER = {
    "key": "a dagger",
    "aliases": ["dagger"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "This dagger is a sharp, threatening blade expertly mounted on "
            "a simple leather-wrapped metal hilt.",
    "weight": 0.5,
    "value": 30*CC,
    "damage": 1,
    "range": "melee"
}

MAUL_HAMMER = {
    "key": "a maul hammer",
    "aliases": ["maul hammer", "maul", "hammer"],
    "typeclass": "typeclasses.weapons.TwoHandedWeapon",
    "desc": "A heavy mass of metal mounted atop a sturdy staff, "
            "ready to deliver crushing blows to your enemies.",
    "weight": 5,
    "value": 2*SC,
    "damage": 4,
    "range": "melee"
}

LANCE_POLEARM = {
    "key": "a lance polearm",
    "aliases": ["lance polearm", "lance", "polearm"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "A sturdy wooden rod fitted with a menacing spike, this "
            "lance polearm threatens even enemies at a distance.",
    "weight": 4,
    "value": 2*SC,
    "damage": 4,
    "range": "reach"
}

PIKE_POLEARM = {
    "key": "a pike polearm",
    "aliases": ["pike polearm", "pike", "polearm"],
    "typeclass": "typeclasses.weapons.TwoHandedWeapon",
    "desc": "Requiring two hands to wield, this long spear was originally "
            "designed to unseat a rider on horseback.",
    "weight": 9,
    "value": 50*CC,
    "damage": 3,
    "range": "reach"
}

MAPLE_STAFF = {
    "key": "a quarterstaff",
    "aliases": ["quarterstaff", "staff"],
    "typeclass": "typeclasses.weapons.TwoHandedWeapon",
    "desc": "Enemies at a distance should be wary of this stout wooden "
            "staff, though it doesn't pack much of a punch. If only it "
            "could be enchanted...",
    "weight": 2,
    "value": 2*CC,
    "damage": 0,
    "range": "reach"
}

MACE_ROD = {
    "key": "a mace",
    "aliases": ["mace", "rod"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "This mace features a crown-shaped head and a slender handle. "
            "It's much lighter than it looks, but still heavy enough to do "
            "some damage.",
    "weight": 2,
    "value": 50*CC,
    "damage": 2,
    "range": "melee"
}

MORNINGSTAR_ROD = {
    "key": "a morningstar",
    "aliases": ["morningstar", "rod"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "This mace's leather-wrappend handle extends up to a large, "
            "spiked metal orb. Its brutal appearance is sure to  "
            "intimidate.",
    "weight": 2,
    "value": 1*SC,
    "damage": 3,
    "range": "melee"
}

SCYTHE = {
    "key": "a scythe",
    "aliases": ["scythe"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "Most often used by farm workers to harvest crops, the "
            "curved blade of this tool can also be used to tear enemies "
            "apart.",
    "weight": 1,
    "vaule": 1*SC,
    "damage": 1,
    "range": "reach"
}

SHORT_SWORD = {
    "key": "a short sword",
    "aliases": ["short sword", "sword"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "Blood stains and dirt smudge the iron blade of this "
            "short sword. Surely it has seen its share of battle.",
    "weight": 1,
    "value": 1*SC,
    "damage": 2,
    "range": "melee"
}

RAPIER = {
    "key": "a rapier",
    "aliases": ["rapier"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "Mottled by age and oxidation, this rapier's blade has seen "
            "better days, but the hilt looks almost new.",
    "weight": 1,
    "value": 3*SC,
    "damage": 3,
    "range": "melee"
}

WHIP = {
    "key": "a whip",
    "aliases": ["whip"],
    "typeclass": "typeclasses.weapons.Weapon",
    "desc": "Sixteen strands of leather, braided tightly in multiple "
            "layers. It extends the user's reach and can be used to disarm.",
    "weight": 1,
    "value": 30*CC,
    "damage": 1,
    "range": "melee"
}


# Ranged Weapons


LONG_BOW = {
    "key": "a long bow",
    "aliases": ["long bow", "bow"],
    "typeclass": "typeclasses.weapons.TwoHandedRanged",
    "desc": "This bow has a rich patina from years of use, but its draw is "
            "firm and it will still accurately deliver an arrow to the heart "
            "of your enemies.",
    "weight": 1,
    "value": 40*CC,
    "damage": 1,
    "ammunition": "arrow",
    "range": "ranged"
}

HAND_CROSSBOW = {
    "key": "a hand crossbow",
    "aliases": ["hand crossbow", "crossbow", "hand"],
    "typeclass": "typeclasses.weapons.RangedWeapon",
    "desc": "This wooden crossbow is compact and powerful. Brazen "
            "adventurers may even choose to dual-wield them.  ",
    "weight": 2,
    "value": 4*SC,
    "damage": 0,
    "ammunition": "quarrel",
    "range": "ranged"
}

LIGHT_CROSSBOW = {
    "key": "a light crossbow",
    "aliases": ["light crossbow", "crossbow", "light"],
    "typeclass": "typeclasses.weapons.TwoHandedRanged",
    "desc": "The laminated wooden recurve of this wooden crossbow fires "
            "quarrels with incredible force and accuracy. ",
    "weight": 3,
    "value": 3*SC,
    "damage": 1,
    "ammunition": "quarrel",
    "range": "ranged"
}

# Ammunition

ARROW = {
    "key": "an obsidian-tipped arrow",
    "aliases": ["arrow"],
    "typeclass": "typeclasses.items.Bundlable",
    "desc": "Arrows crafted from reed wood and obsidian stone.",
    "weight": 1,
    "value": 2*CC,
    "bundle_size": 10,
    "prototype_name": "ARROW"
}

QUARREL = {
    "key": "a crossbow quarrel",
    "aliases": ["quarrel", "qua"],
    "typeclass": "typeclasses.items.Bundlable",
    "desc": "A quarrel for use in a crossbow.",
    "weight": 0.5,
    "value": 3*CC,
    "bundle_size": 10,
    "prototype_name": "QUARREL"
}

ARROW_BUNDLE = {
    "key": "a bundle of arrows",
    "aliases": ["bundle of arrows", "bundle arrow", "arrows"],
    "typeclass": "typeclasses.items.Bundle",
    "desc": "A bundle of arrows held together with a thin leather strap.",
    "weight": 10,
    "value": 25*CC,
    "quantity": 10,
    "prototype_name": "ARROW",
}

QUARREL_BUNDLE = {
    "key": "a bundle of quarrels",
    "aliases": ["bundle of quarrels", "bundle quarrel", "quarrels"],
    "typeclass": "typeclasses.items.Bundle",
    "desc": "A bundle of quarrels held together with a thin leather strap.",
    "weight": 5,
    "value": 30*CC,
    "quantity": 10,
    "prototype_name": "QUARREL",
}

# Thrown Ranged

THROWING_AXE = {
    "key": "a throwing axe",
    "aliases": ["throwing axe", "th axe", "thr axe", "axe"],
    "typeclass": "typeclasses.weapons.RangedWeapon",
    "desc": "This axe is light and sharp. It is balanced to spin fast "
            "and true when thrown.",
    "weight": 2,
    "value": 80*CC,
    "damage": 0,
    "range": "reach",
    "ammunition": "throwing axe"
}

THROWING_DAGGER = {
    "key": "a throwing dagger",
    "aliases": ["throwing dagger", "th dagger", "thr dagger" "dagger"],
    "typeclass": "typeclasses.weapons.RangedWeapon",
    "desc": "This small, easily-concealed dagger flies straight and "
            "silently when thrown by a skilled assassin.",
    "weight": 1,
    "value": 30*CC,
    "damage": 0,
    "range": "reach",
    "ammunition": "throwing dagger"
}

TRIDENT = {
    "key": "a trident",
    "aliases": ["trident"],
    "typeclass": "typeclasses.weapons.RangedWeapon",
    "desc": "The trident's triple-pointed metal spearhead is heavy and "
            "inflicts the most damage of the thrown weapons.",
    "weight": 2,
    "value": 1*SC,
    "damage": 2,
    "range": "reach",
    "ammunition": "trident"
}

JAVELIN = {
    "key": "a javelin",
    "aliases": ["javelin"],
    "typeclass": "typeclasses.weapons.RangedWeapon",
    "desc": "Long and light, the javelin has the longest range of thrown "
            "weapons.",
    "weight": 1,
    "value": 15*CC,
    "damage": 1,
    "ammunition": "javelin",
    "range": "ranged",
}
