"""
Weapon typeclasses
"""

from typeclasses.items import Equippable
from evennia.typeclasses.attributes import AttributeProperty


class Weapon(Equippable):
    """
    Typeclass for weapon objects.

    Attributes:
        damage (int): primary attack stat
        handedness (int): indicates single- or double-handed weapon
    """
    # points of damage the weapon does
    damage = AttributeProperty(default=0)
    # how many slots the weapon uses
    handedness = AttributeProperty(default=1)
    # how long a cooldown after being used
    cooldown = AttributeProperty(default=1)

    def at_object_creation(self):
        super().at_object_creation()
        self.slots = ['wield1', 'wield2']
        self.db.messages = {
            'dmg_hp': "{actor} attacks {target} with {weapon}, striking a painful blow.",
            'dmg_sp': "{actor} stuns {target} with {weapon}.",
            'dodged': "{weapon} fails to meet its target as {target} dodges {actor}'s attack.",
            'missed': "{actor} attacks {target} with {weapon} and misses."
        }

    def at_attack(self, character, range):
        if not self.tags.has(range, category="combat_range"):
            # can't be used for this kind of attack
            return (0, 0)
        # add stat bonuses here?
        return (self.damage, self.cooldown)

    def load_ammunition(self):
        """Checks whether there is proper ammunition and returns one unit."""
        if ammo_type := self.db.ammunition:
            ammunition = [obj for obj in self.location.contents
                          if obj.is_typeclass('typeclasses.items.Bundlable')
                              or any(obj.tags.has(ammo, category="ammunition"))]

            if not ammunition:
                # no individual ammo found, search for bundle
                bundle = [obj for obj in self.location.contents
                          if "bundle {}".format(ammo_type)
                              in obj.aliases.all()
                          and obj.is_typeclass('typeclasses.items.Bundle')]

                if bundle:
                    bundle = bundle[0]
                    bundle.expand()
                    return self.get_ammunition_to_fire()
                else:
                    return None
            else:
                return ammunition[0]

        else:
            # no valid ammo for this weapon
            return None

