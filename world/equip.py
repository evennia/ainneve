# -*- coding: UTF-8 -*-
from evennia import settings, utils
 
DEFAULT = ('head',
           'left ear',
           'right ear',
           'body',
           'left hand',
           'right hand',
           'holds')

class EquipHandler(object):
    """
    Simple handler for characters equipment.
    This is actually an interface to easily read, write and manage
    the equipment of a character. Slots/objects can be accessed by
    getter and setter methods.
    Add and remove methods are also present, they add a little bit
    of error checking to the set method.
    The handler can also check for the presence of an item in the equip
    with the simple syntax `obj in char.equip` and it is iterable.
    To implement it add it to the main character
    typeclass as a property:
    
    `
    from world.equip import EquipHandler
    
    @property
    def equip(self):
        return EquipHandler(self, list_of_slots)
    `
    
    list_of_slots is a list or a tuple of named slots
    
    Also see commands/equip_commands.py for the commands
    related to this handler.


    EquipHandler attributes:
    
        obj:    the parent typeclass
        slots:  a tuple of slots available for the character

    EquipHandler methods:
        add(item):          add an item to the equipment, returns True
                            if the item is successfully equipped
        remove(item)        remove an item from the equipment, returns
                            True if the item is correctly removed.
        get(slot):          returns the item in the corresponding slot,
                            if present, otherwise returns None
        set(slot, item):    set an item in the corresponding slot,
                            raise ValueError if the item can't be set
                            in equip, raise KeyError if slot is not
                            already defined in equip. This set method
                            replace objects in equipment, use the remove
                            method to correctly handle real-life
                            situations
        items():            returns a list of equipped items. Does not
                            returns unoccupied slots
        empty_slots():      returns a list of empty slots

    Example usage:
        Say obj is a hat.
        > obj in character.equip
        False
        > character.equip.add(obj)
        True
        > obj in equip
        True
        > for slot, item in character.equip:
        >     print "%s: %s" % (slot, item)
        head: a hat
        > character.equip.remove(obj)
        True
        

    """
    def __init__(self, obj, slots=DEFAULT):
        """
        Init class.
        """
        # save the parent typeclass
        self.obj = obj
        # available slots
        self.slots = tuple(set(slots))
        # initialize equipment
        if not self.obj.db.equip:
            self.obj.db.equip = {x: None for x in self.slots}

    def _set(self, slot, item):
        """
        set an item in the corresponding slot, raise ValueError if the
        item can't be set in equip, raise KeyError if slot is not already
        defined in equip. This set method replace objects in equipment,
        use the remove method to correctly handle real-life situations.
        """
        # allows None values to pass all checks
        if item != None:
            # first check, only allows typeclasses to pass;
            # at the same time all expected errors are converted
            # to ValueError
            try:
                if not item.is_typeclass(settings.BASE_OBJECT_TYPECLASS,
                                         exact=False):
                    raise AttributeError
            except AttributeError:
                raise ValueError("Item can't be set in equip.")
            # second check, only allows objects that are
            # correctly defined to be equipped, i.e. they have a slot
            # and that slot exist in the current equip.
            # At the same time all expected errors are converted
            # to KeyError
            try:
                if slot not in self.slots:
                    raise TypeError
            except TypeError:
                raise KeyError("Slot not available: %s" % slot)
        self.obj.db.equip[slot] = item

    # implement the set method
    set = _set

    def _get(self, slot, default=None):
        """
        Getter method. Returns the item in the corresponding slot,
        if present, otherwise returns `default`
        """
        return self.obj.db.equip.get(slot, default)

    # implement the get method
    get = _get

    def __len__(self):
        """
        Returns the number of equipped objects.
        """
        return len(self.items())

    def __str__(self):
        """
        Shows the equipment.
        """
        return str(self.showtable())

    def __iter__(self):
        """
        Iterate over the equip in an ordered way.
        """
        if not self.slots:
            return
        for slot in self.slots:
                yield (slot, self.obj.db.equip.get(slot))

    def __contains__(self, item):
        """
        Implement the __contains__ method.
        """
        return item in self.items()

    def items(self):
        """
        Shows equipped items.
        """
        return filter(None, self.obj.db.equip.values())

    def empty_slots(self):
        """
        Returns empty slots.
        """
        return filter(lambda x: self.obj.db.equip[x] is None, \
                      self.obj.db.equip.keys())

    def add(self, obj):
        """ 
        Add an object to character's equip.
        """
        slots = utils.make_iter(obj.db.slot)
        free_slots = [sl for sl in slots if self.get(sl, True) == None]
        if not free_slots:
            return False
        slot = free_slots[0]
        self._set(slot, obj)
        return True

    def hold(self, obj):
        """ 
        Add an object to the 'hold' slot of character's equip.
        """
        
    def remove(self, obj):
        """ 
        Remove an object from character's equip.
        """
        for slot, item in self:
            if item == obj:
                self._set(slot, None)
                return True
        return False



