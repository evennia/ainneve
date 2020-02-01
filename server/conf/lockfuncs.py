"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

from typeclasses.combat_handler import COMBAT_DISTANCES

def in_combat(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if an active combat handler is present"""
    if hasattr(accessing_obj, 'nattributes') and \
            accessing_obj.nattributes.has('combat_handler'):
        return True
    else:
        return False


def in_range(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj has any targets in specified range"""
    range = args[0] if args else 0
    if isinstance(range, str):
        range = COMBAT_DISTANCES.indexof(range)
    if range < 0:
        return False
    if hasattr(accessing_obj, 'nattributes') and \
            accessing_obj.nattributes.has('combat_handler'):
        ch = accessing_obj.ndb.combat_handler
        return any(y <= range for x,y in ch.db.distances.iteritems()
                    if accessing_obj.id in x)
    return False


def melee_equipped(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj has a melee weapon equipped"""
    if hasattr(accessing_obj, 'equip'):
        return any(
            y.is_typeclass('typeclasses.weapons.Weapon', exact=True) or
            y.is_typeclass('typeclasses.weapons.TwoHandedWeapon', exact=True)
            for _, y in accessing_obj.equip
        )

def ranged_equipped(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj hsa a ranged weapon equipped"""
    if hasattr(accessing_obj, 'equip'):
        return any(
            y.is_typeclass('typeclasses.weapons.RangedWeapon', exact=True) or
            y.is_typeclass('typeclasses.weapons.TwoHandedRanged', exact=True)
            for _, y in accessing_obj.equip
        )
