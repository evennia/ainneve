"""
Helpers for testing evadventure modules.

"""

from evennia.utils import create

from world import enums
from typeclasses.characters import Character
from typeclasses.objects import (
    ArmorObject,
    Helmet,
    Object,
    Shield,
    WeaponObject,
)


class AinneveTestMixin:
    """
    Provides a set of pre-made characters.

    """

    def setUp(self):
        super().setUp()
        # remove default dev permissions from first test account so test chars have equivalent perms
        self.account.permissions.remove('Developer')

        self.helmet = create.create_object(
            Helmet,
            key="helmet",
        )
        self.shield = create.create_object(
            Shield,
            key="shield",
        )
        self.armor = create.create_object(
            ArmorObject,
            key="armor",
        )
        self.weapon = create.create_object(
            WeaponObject,
            key="weapon",
        )
        self.big_weapon = create.create_object(
            WeaponObject,
            key="big_weapon",
            attributes=[("inventory_use_slot", enums.WieldLocation.TWO_HANDS)],
        )
        self.item = create.create_object(Object, key="backpack item")
