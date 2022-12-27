"""
Prototypes

"""

# base room prototype for XYZGrid rooms in ainneve
AINNEVE_XYZ_ROOM = {
        "prototype_parent": "xyz_room",
        "prototype_key": "ainneve_xyz_room",
        "typeclass": "typeclasses.rooms.TownRoom",
    }

RIVERPORT_XYZ_ROOM = {
        "prototype_parent": "ainneve_xyz_room",
        "prototype_key": "riverport_xyz_room",
        "typeclass": "typeclasses.rooms.TownRoom",
        "tags": [('riverport_settlement', 'area_id')]
    }


LANDMARK_RIVERPORT_ROOM = {
    "prototype_key": "landmark_riverport_room",
    "desc": "You are standing in front of the city gates.",
}



## example of module-based prototypes using
## the variable name as `prototype_key` and
## simple Attributes

# from random import randint
#
# GOBLIN = {
# "key": "goblin grunt",
# "health": lambda: randint(20,30),
# "resists": ["cold", "poison"],
# "attacks": ["fists"],
# "weaknesses": ["fire", "light"],
# "tags": = [("greenskin", "monster"), ("humanoid", "monster")]
# }
#
# GOBLIN_WIZARD = {
# "prototype_parent": "GOBLIN",
# "key": "goblin wizard",
# "spells": ["fire ball", "lighting bolt"]
# }
#
# GOBLIN_ARCHER = {
# "prototype_parent": "GOBLIN",
# "key": "goblin archer",
# "attacks": ["short bow"]
# }
#
# This is an example of a prototype without a prototype
# (nor key) of its own, so it should normally only be
# used as a mix-in, as in the example of the goblin
# archwizard below.
# ARCHWIZARD_MIXIN = {
# "attacks": ["archwizard staff"],
# "spells": ["greater fire ball", "greater lighting"]
# }
#
# GOBLIN_ARCHWIZARD = {
# "key": "goblin archwizard",
# "prototype_parent" : ("GOBLIN_WIZARD", "ARCHWIZARD_MIXIN")
# }
