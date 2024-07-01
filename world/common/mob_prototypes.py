import random

BASE_MOB = {
    "prototype_key": "base_mob",
    "typeclass": "typeclasses.mobs.mob.BaseMob",
}

BASE_MOB_GOBLIN = {
    "prototype_parent": "base_mob",
    "prototype_key": "base_mob_goblin",
}

MOB_GOBLIN_WEAK = {
    "prototype_parent": "base_mob_goblin",
    "prototype_key": "mob_goblin_weak",
    "prototype_tags": [("trash", "archetype"),],
    "key": "small goblin",
    "cclass_key": "rogue",
    "race_key": "goblin",
    "hp_max": 1,
    "mana_max": 1,
    "xp_factor": 0.1,
    "starting_equipment_prototypes": [
        "weapon_dagger_common"
    ],
    "mob_scaling": {"strength": 0.1, "cunning": 0.2, "will": 0.1, "hp": 0.1, "mana": 0.1}
}

MOB_GOBLIN_COMMON = {
    "prototype_parent": "base_mob_goblin",
    "prototype_key": "mob_goblin_common",
    "prototype_tags": [("common", "archetype"),],
    "key": "goblin",
    "cclass_key": "rogue",
    "race_key": "goblin",
    "starting_equipment_prototypes": [
        "weapon_dagger_common"
    ],
    "hp_max": lambda: random.randint(2, 5),
    "mana_max": 1,
    "xp_factor": 0.2,
    "mob_scaling": {"strength": 0.2, "cunning": 0.5, "will": 0.2, "hp": 0.5, "mana": 0.1}
}

MOB_GOBLIN_WARRIOR = {
    "prototype_parent": "base_mob_goblin",
    "prototype_key": "mob_goblin_warrior",
    "prototype_tags": [("tough", "archetype"),],
    "key": "goblin warrior",
    "cclass_key": "rogue",
    "race_key": "goblin",
    "starting_equipment_prototypes": [
        "weapon_sword_common",
        "armor_leather_common",
    ],
    "hp_max": lambda: random.randint(5, 7),
    "mana_max": lambda: random.randint(1, 5),
    "xp_factor": 0.5,
    "mob_scaling": {"strength": 0.5, "cunning": 0.75, "will": 0.5, "hp": 0.75, "mana": 0.5}
}

MOB_GOBLIN_WARCHIEF = {
    "prototype_parent": "base_mob_goblin",
    "prototype_key": "mob_goblin_warchief",
    "prototype_tags": [("special", "archetype"),],
    "key": "goblin warchief",
    "cclass_key": "rogue",
    "race_key": "goblin",
    "starting_equipment_prototypes": [
        "weapon_sword_common",
        "shield_round_common",
        "armor_iron_common",
        "helmet_iron_helm_common",
    ],
    "hp_max": lambda: random.randint(8, 10),
    "mana_max": lambda: random.randint(7, 10),
    "xp_factor": 0.75,
    "mob_scaling": {"strength": 0.75, "cunning": 1, "will": 0.75, "hp": 1, "mana": 0.75}
}
