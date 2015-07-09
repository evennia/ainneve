"""
Generic items
"""
from typeclasses.objects import Object

class Item(Object):
    """
    This class implements a basic item.

    """
    def at_object_creation(self):
        """
        Setup item-specific variables.
        """
        super(Item, self).at_object_creation()
        self.locks.add("equip:false();hold:false()")

    def at_hold(self, character):
        """
        Hook called when a character holds this object.

        Args:
            character - the character holding this object

        """
        pass


class EquippableItem(Item):
    """
    This class implements an item that can be set in the equipment.

    """
    slot = None
    slot_operator = 'OR'

    def at_object_creation(self):
        """
        Setup item-specific variables.
        """
        super(EquippableItem, self).at_object_creation()
        self.locks.add("equip:all()")
        self.self.db.slot_operator = self.slot_operator
        self.db.slot = self.slot

    def at_equip(self, character):
        """
        Hook called when an object is equipped by character.

        Args:
            character - the character equipping this object

        """
        pass

    def at_remove(self, character):
        """
        Hook called when an object is removed from character equip.
        
        Args:
            character - the character removing this object

        """
        pass

#
# Armors
#

class Armor(EquippableItem):
    """
    This class implements a basic armor object

    """
    armor_type = 'other'

    def at_object_creation(self):
        """
        Setup weapon-specific variables.
        """
        super(Armor, self).at_object_creation()
        self.locks.add("equip:all()")
        self.tags.add(self.armor_type, category='armor')

class Shield(Armor):
    """
    This class implements a basic shield object,
    a functional type of armor.

    """
    armor_type = 'shield'
    slot = 'wield2'

class BreastPlate(Armor):
    """
    This class implements a basic shield object,
    a functional type of armor.

    """
    armor_type = 'breastplate'
    slot = 'torso'

#
# Weapons
#

class Weapon(EquippableItem):
    """
    This class implements a basic weapon object

    """
    weapon_type = 'other'
    slot = 'wield1'

    def at_object_creation(self):
        """
        Setup weapon-specific variables.
        """
        super(Weapons, self).at_object_creation()
        self.locks.add("equip:all()")
        self.tags.add(self.weapon_type, category='weapon')


class MeleeWeapon(Weapon):
    """
    This class implements a basic melee weapon.

    """
    pass

class TwoHandedWeapon(Weapon):
    """
    This class implements a basic two-handed weapon object.

    """
    weapon_type = 'other'
    slot = ['wield1', 'wield2']
    slot_operator = 'AND'


class RangedWeapon(TwoHandedWeapon):
    """
    This class implements a basic ranged weapon

    """
    pass

class Dagger(MeleeWeapon):
    """
    This class implements a basic dagger object

    """
    weapon_type = 'dagger'

class Sword(MeleeWeapon):
    """
    This class implements a basic sword object

    """
    weapon_type = 'sword'

class TwoHandedSword(Sword, TwoHandedWeapon):
    """
    This class implements a basic sword object

    """
    pass

class Axe(MeleeWeapon):
    """
    This class implements a basic axe object

    """
    weapon_type = 'axe'

class Mace(MeleeWeapon):
    """
    This class implements a basic mace object

    """
    weapon_type = 'mace'

class Bow(RangedWeapon):
    """
    This class implements a basic sword object

    """
    weapon_type = 'bow'

