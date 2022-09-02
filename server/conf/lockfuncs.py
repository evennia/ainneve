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


def in_combat(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if an active combat handler is present"""
    if hasattr(accessing_obj, 'nattributes'):
        return accessing_obj.nattributes.has('combat')
    else:
        return False


def in_range(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj has any targets in specified range"""
    range = args[0] if args else "melee"
    if hasattr(accessing_obj, 'nattributes'):
        combat = accessing_obj.ndb.combat
        if not combat:
            return False
        return combat.any_in_range(accessing_obj, range)
    else:
        return False


def melee_equipped(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj has a melee weapon equipped"""
    if hasattr(accessing_obj, 'equip'):
        return any(
            y.tags.has("melee", category="combat_range") for _, y in accessing_obj.equip
        )
    else:
      return False


def ranged_equipped(accessing_obj, accessed_obj, *args, **kwargs):
    """returns true if accessing_obj hsa a ranged weapon equipped"""
    if hasattr(accessing_obj, 'equip'):
        return any(
            y.tags.has("ranged", category="combat_range") for _, y in accessing_obj.equip
        )
    else:
      return False
