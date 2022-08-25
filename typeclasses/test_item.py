from evennia.utils.test_resources import EvenniaTest
from typeclasses.items import Item, Equippable, Bundle, Bundlable
from typeclasses.characters import Character
from typeclasses.armors import Armor
from evennia import create_object
from utils.utils import sample_char
from mock import Mock


class ItemTestCase(EvenniaTest):
    """
    Test case for items:
    A non-equippable Item
    An Equippable Item, whose typeclass will be modified to Armor for Equipping testing
    Bundlable Item,
    Bundle of Bundlable Item
    """
    bundlable_typeclass = Bundlable
    item_typeclass = Item
    chestplate_initial_typeclass = Equippable
    chestplate_typeclass = Armor
    character_typeclass = Character

    item_name = "item"
    chestplate_name = "chestplate"
    bundle_name = "bundle"
    bundlable_name = "bundlable"

    def setUp(self):
        """
        Create non-equippable item for testing
        Create equippable item for testing,
        it inherits from Armor, whose parent is the typeclass Equippable
        """
        super(ItemTestCase, self).setUp()
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        self.char1.msg = Mock()
        self.item = create_object(
            self.item_typeclass, key=self.item_name, location=self.char1)
        self.chestplate = create_object(
            self.chestplate_initial_typeclass, key=self.chestplate_name, location=self.char1)
        self.bundlable = create_object(
            self.bundlable_typeclass, key=self.bundlable_name, location=self.char1)

    def test_init_items(self):
        """
        Tests item's intial values: item's value, 
        weight as well as the locks added onto it
        """
        self.assertEqual(self.item.value, 0,
                         f"{self.item.key}'s value was not initialized")
        self.assertEqual(self.item.weight, 0.0,
                         f"{self.item.key} weight was not initialized")
        self.assertEqual(self.item.locks.get(), "call:true();"
                                                "control:perm(Developer);"
                                                "delete:perm(Admin);"
                                                "drop:holds();"
                                                "edit:perm(Admin);"
                                                "equip:false();"
                                                "examine:perm(Builder);"
                                                "get:true();"
                                                "puppet:perm(Wizards);"
                                                "tell:perm(Admin);"
                                                "view:all()",
                         "Locks were not intialized")

        self.assertEqual(self.chestplate.value, 0,
                         f"{self.chestplate.key}'s value was not initialized")
        self.assertEqual(self.chestplate.weight, 0.0,
                         f"{self.item.key}'s weight was not initialized")
        self.assertEqual(self.chestplate.locks.get(), "call:true();"
                         "control:perm(Developer);"
                         "delete:perm(Admin);"
                         "drop:holds();"
                         "edit:perm(Admin);"
                         "equip:true();"
                         "examine:perm(Builder);"
                         "get:true();"
                         "puppet:false();"
                         "tell:perm(Admin);"
                         "view:all()",
                         "Locks were not intialized")
        self.assertEqual(self.chestplate.db.slots, None,
                         "Slots does not equal None")
        self.assertEqual(self.chestplate.db.multi_slot, False,
                         "Slots are multi slots when it's supposed to be false")
        self.assertEqual(self.chestplate.db.used_by,
                         None, f"{self.chestplate.key} is equipped")
        
        self.assertEqual(self.bundlable.db.bundle_size, 999, f"{self.bundlable.key}'s bundle size was not initialized")
        self.assertEqual(self.bundlable.db.prototype_name, None, f"{self.bundlable.key}'s prototype name was not initalized")

        

    def test_get_items(self):
        """
        Tests items being retrieved and that
        values are accurately reflected
        """
        self.char1.execute_cmd(f"get {self.item.key}")
        self.assertTrue(self.item in self.char1.contents,
                        f"{self.item.key} was not retrieved")
        self.assertEqual(self.char1.traits.ENC.current,
                         0, f"{self.item.key} was not weightless")
        self.assertEqual(self.char1.traits.MV.mod, 0, "Movement was affected")

        self.char1.execute_cmd(f"get {self.chestplate.key}")
        self.assertTrue(self.chestplate in self.char1.contents,
                        f"{self.chestplate.key} was not retrieved")
        self.assertEqual(self.char1.traits.ENC.current, 0,
                         f"{self.chestplate.key} was not weightless")
        self.assertEqual(self.char1.traits.MV.mod, 0, "Movement was affected")

    def test_drop_items(self):
        """
        Tests item being dropped as well as the resulting
        change of values in char1
        """
        self.char1.execute_cmd(f"drop {self.item.key}")
        self.assertFalse(self.item in self.char1.contents,
                         f"{self.item.key} was not dropped")
        self.assertEqual(self.char1.traits.ENC.current,
                         0, f"{self.item.key} affected weight")
        self.assertEqual(self.char1.traits.MV.mod, 0, "Movement was affected")

        self.char1.execute_cmd(f"drop {self.chestplate.key}")
        self.assertFalse(self.chestplate in self.char1.contents,
                         f"{self.chestplate.key} was not dropped")
        self.assertEqual(self.char1.traits.ENC.current,
                         0, f"{self.chestplate.key} affected weight")
        self.assertEqual(self.char1.traits.MV.mod, 0, "Movement was affected")

    def test_equip_items(self):
        """
        Tests that equippable items can be equipped
        Tests that non-equippable items should not be equipped
        """
        self.char1.execute_cmd("get item")
        self.char1.execute_cmd("get chestplate")
        self.assertTrue(self.item in self.char1.contents,
                        f"{self.item.key} was not retrieved")
        self.assertTrue(self.chestplate in self.char1.contents,
                        f"{self.chestplate.key} was not retrieved")

        self.char1.execute_cmd(f"equip {self.item.key}")
        self.assertFalse(self.item in self.char1.equip,
                         f"Unequippable {self.item.key} was equipped")

        # Change Equippable typeclass to Armor so Equipping items can be tested
        self.chestplate.swap_typeclass(self.chestplate_typeclass, clean_attributes=False,
                                       run_start_hooks="all", no_default=True, clean_cmdsets=False)
        self.assertEqual(self.chestplate.db.slots,
                         ['armor'], "Slot was not set")
        self.assertEqual(self.chestplate.db.toughness, 0, "Toughness was initialized")

        self.char1.execute_cmd(f"equip {self.chestplate.key}")
        self.assertTrue(self.chestplate in self.char1.equip, f"{self.chestplate.key} was not equipped")

    def test_remove_item(self):
        """
        Tests that item is being unequipped
        """
        self.chestplate.swap_typeclass(self.chestplate_typeclass, clean_attributes=False,
                                       run_start_hooks="all", no_default=True, clean_cmdsets=False)
        self.char1.execute_cmd(f"equip {self.chestplate.key}")
        self.assertTrue(self.chestplate in self.char1.equip, f"{self.chestplate.key} was not equipped")
        self.char1.execute_cmd(f"remove {self.chestplate.key}")
        self.assertFalse(self.chestplate in self.char1.equip, f"{self.chestplate.key} was not unequipped")
        self.assertTrue(self.chestplate in self.char1.contents, f"{self.chestplate.key} is not in inventory")

    def test_drop_item(self):
        """
        Tests that dropping equipped item drops it out of character's inventory
        """
        self.chestplate.swap_typeclass(self.chestplate_typeclass, clean_attributes=False,
                                       run_start_hooks="all", no_default=True, clean_cmdsets=False)
        self.char1.execute_cmd(f"equip {self.chestplate.key}")
        self.assertTrue(self.chestplate in self.char1.equip, f"{self.chestplate.key} was not equipped")
        self.char1.execute_cmd(f"drop {self.chestplate.key}")
        self.assertFalse(self.chestplate in self.char1.equip, f"{self.chestplate.key} was not unequipped")
        self.assertFalse(self.chestplate in self.char1.contents, f"{self.chestplate.key} was not dropped")



        
