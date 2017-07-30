def find_parent(obj, condition):
    '''
    Find the parent of the object `obj` that matches `condition`.

    `obj` is an Evennia game object.
    `condition` is a function that returns `True` if the parent matches
        the condition, or `False` otherwise.
    Alternatively, `condition` can be a string representing the typeclass
        the parent must match.

    This function returns the parent that matches the condition,
    or `None` if no parent matches.
    '''
    loc = obj.location
    if loc is None: return loc

    if isinstance(condition, (str, unicode)):
        tc = condition
        condition = lambda loc: loc.is_typeclass(tc)

    seen = set()

    done = False
    while 1:
        if loc in seen:
            # if the loop already looked at this location
            # and disqualified it, the parent chain is circular,
            # and there is nothing in the parent chain
            # that satisfies the condition.
            return None
        if loc is None:
            return None
        if condition(lock):
            break
        else:
            seen.add(loc)
            loc = loc.location
    return loc

def find_room(obj):
    return find_parent(obj, 'rooms.Room')

def find_character(obj):
    return find_parent(obj, 'characters.Character')
