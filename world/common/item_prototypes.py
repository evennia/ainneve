from world.enums import WieldLocation, CombatRange, Ability

BASE_WEAPON = {
    "prototype_key": "base_weapon",
    "typeclass": "typeclasses.objects.WeaponObject",
    "inventory_use_slot": WieldLocation.WEAPON_HAND,
    "quality": 3,
}

BASE_WEAPON_MELEE = {
    "prototype_parent": "base_weapon",
    "prototype_key": "base_weapon_melee",
    "attack_range": CombatRange.MELEE,
    "defense_type": Ability.ARMOR,
}

WEAPON_DAGGER_COMMON = {
    "prototype_parent": "base_weapon_melee",
    "prototype_key": "weapon_dagger_common",
    "key": "dagger",
    "attack_type": Ability.CUN,
    "damage_roll": "1d6",
}

WEAPON_SWORD_COMMON = {
    "prototype_parent": "base_weapon_melee",
    "prototype_key": "weapon_sword_common",
    "key": "sword",
    "attack_type": Ability.STR,
    "damage_roll": "1d6"
}

WEAPON_AXE_COMMON = {
    "prototype_parent": "base_weapon_melee",
    "prototype_key": "weapon_axe_common",
    "key": "axe",
    "attack_type": Ability.STR,
    "damage_roll": "1d6"
}

WEAPON_TELEKINETIC_STONE_COMMON = {
    "prototype_parent": "base_weapon_melee",
    "prototype_key": "weapon_tk_stone_common",
    "key": "telekinetic stone",
    "attack_type": Ability.WIL,
    "damage_roll": "1d4"
}


BASE_ARMOR = {
    "prototype_key": "base_armor",
    "typeclass": "typeclasses.objects.ArmorObject",
    "inventory_use_slot": WieldLocation.BODY,
    "quality": 3,
}

ARMOR_LEATHER_COMMON = {
    "prototype_parent": "base_armor",
    "prototype_key": "armor_leather_common",
    "key": "Leather Armor",
    "inventory_use_slot": WieldLocation.BODY,
    "armor": 1,
}

ARMOR_IRON_COMMON = {
    "prototype_parent": "base_armor",
    "prototype_key": "armor_iron_common",
    "key": "Iron Armor",
    "inventory_use_slot": WieldLocation.BODY,
    "armor": 2,
}

ARMOR_ROBES_COMMON = {
    "prototype_parent": "base_armor",
    "prototype_key": "armor_robes_common",
    "key": "Robes",
    "inventory_use_slot": WieldLocation.BODY,
    "armor": 0,
}

BASE_SHIELD = {
    "prototype_key": "base_shield",
    "typeclass": "typeclasses.objects.Shield",
    "inventory_use_slot": WieldLocation.SHIELD_HAND,
    "quality": 3,
}

SHIELD_BUCKLER_COMMON = {
    "prototype_parent": "base_shield",
    "prototype_key": "shield_buckler_common",
    "key": "buckler",
}

SHIELD_ROUND_COMMON = {
    "prototype_parent": "base_shield",
    "prototype_key": "shield_round_common",
    "key": "round shield",
}

BASE_HELMET = {
    "prototype_key": "base_helmet",
    "typeclass": "typeclasses.objects.Helmet",
    "inventory_use_slot": WieldLocation.HEAD,
    "quality": 3,
}

HELMET_LEATHER_HOOD_COMMON = {
    "prototype_parent": "base_helmet",
    "prototype_key": "helmet_leather_hood_common",
    "key": "Leather Hood",
}

HELMET_IRON_HELM_COMMON = {
    "prototype_parent": "base_helmet",
    "prototype_key": "helmet_iron_helm_common",
    "key": "Iron Helm",
}
