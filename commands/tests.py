"""
Command test module
"""
import re

from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import EvenniaTest

from commands.building import CmdSetTraits, CmdSetSkills
from commands.chartraits import CmdSheet, CmdTraits
from commands.equip import *
from commands.room_exit import CmdCapacity, CmdTerrain
from typeclasses.characters import Character, NPC
from typeclasses.rooms import Room
from typeclasses.weapons import Weapon
from utils.utils import sample_char
from world.archetypes import apply_archetype, calculate_secondary_traits

# This is used to parse CmdTraits outputs into a dict we can Test
_TRAITS_MATCH_REGEX = re.compile(r"(\w*\s\w*\s*[:]\s*\d)")


class ItemEncumbranceTestCase(EvenniaTest):
    """Test case for at_get/at_drop hooks."""
    character_typeclass = Character
    object_typeclass = Weapon

    def setUp(self):
        super(ItemEncumbranceTestCase, self).setUp()
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        self.obj1.db.desc = 'Test Obj'
        self.obj1.db.damage = 1
        self.obj1.db.weight = 1.0
        self.obj2.swap_typeclass('typeclasses.armors.Armor',
                                 clean_attributes=True,
                                 run_start_hooks="all")
        self.obj2.db.toughness = 1
        self.obj2.db.weight = 18.0

    def test_get_item(self):
        """test that item get hook properly affects encumbrance"""
        self.assertEqual(self.char1.traits.ENC.actual, 0)
        self.assertEqual(self.char1.traits.MV.actual, 5)
        self.char1.execute_cmd('get Obj')
        self.assertEqual(self.char1.traits.ENC.actual, 1.0)
        self.assertEqual(self.char1.traits.MV.actual, 5)
        # Obj2 is heavy enough to incur a movement penalty
        self.char1.execute_cmd('get Obj2')
        self.assertEqual(self.char1.traits.ENC.actual, 19.0)
        self.assertEqual(self.char1.traits.MV.actual, 4)

    def test_drop_item(self):
        """test that item drop hook properly affects encumbrance"""
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('get Obj2')
        self.assertEqual(self.char1.traits.ENC.actual, 19.0)
        self.assertEqual(self.char1.traits.MV.actual, 4)
        self.char1.execute_cmd('drop Obj2')
        self.assertEqual(self.char1.traits.ENC.actual, 1.0)
        self.assertEqual(self.char1.traits.MV.actual, 5)


class EquipTestCase(CommandTest):
    """Test case for EquipHandler and commands."""
    character_typeclass = Character
    object_typeclass = Weapon

    def setUp(self):
        super(EquipTestCase, self).setUp()
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        self.obj1.db.desc = 'Test Obj'
        self.obj1.db.damage = 1
        self.obj1.db.weight = 1.0
        self.obj2.db.desc = 'Test Obj2'
        self.obj2.swap_typeclass('typeclasses.armors.Armor',
                                 clean_attributes=True,
                                 run_start_hooks="all")
        self.obj2.db.toughness = 1
        self.obj2.db.weight = 2.0

    def test_wield_1h_weapon(self):
        """test wield command for 1H weapons"""
        # can't wield from the ground
        self.call(CmdWield(), 'Obj', "You don't have 'Obj' in your inventory.")
        # pick it up to wield the weapon
        self.char1.execute_cmd('get Obj')
        self.call(CmdWield(), 'Obj', "You wield Obj(#4).")
        # test the at_equip hooks
        self.assertEqual(self.char1.traits.ATKM.actual, 8)
        self.assertEqual(self.char1.equip.get('wield1'), self.obj1)
        self.assertIs(self.char1.equip.get('wield2'), None)
        # can't wield armor
        self.char1.execute_cmd('get Obj2')
        self.call(CmdWield(), 'Obj2', "You can't wield Obj2(#5).")

    def test_wield_2h_weapon(self):
        """test wield command for 2H weapons"""
        self.obj1.swap_typeclass('typeclasses.weapons.TwoHandedWeapon',
                                 clean_attributes=True,
                                 run_start_hooks="all")
        self.obj1.db.damage = 1
        self.obj1.db.weight = 1.0
        # pick it up to wield the weapon
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('wield Obj')
        # test the at_equip hooks
        self.assertEqual(self.char1.traits.ATKM.actual, 8)
        self.assertEqual(self.char1.equip.get('wield1'), self.obj1)
        self.assertEqual(self.char1.equip.get('wield2'), self.obj1)

    def test_wield_1h_ranged(self):
        """test wield command for 1H ranged weapons"""
        self.obj1.swap_typeclass('typeclasses.weapons.RangedWeapon',
                                 clean_attributes=True,
                                 run_start_hooks="all")
        self.obj1.db.damage = 1
        self.obj1.db.weight = 1.0
        self.obj1.db.range = 5
        # pick it up to wield the weapon
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('wield Obj')
        # test the at_equip hooks
        self.assertEqual(self.char1.traits.ATKR.actual, 4)
        self.assertEqual(self.char1.equip.get('wield1'), self.obj1)
        self.assertIs(self.char1.equip.get('wield2'), None)

    def test_wield_2h_ranged(self):
        """test wield command for 2H ranged weapons"""
        self.obj1.swap_typeclass('typeclasses.weapons.TwoHandedRanged',
                                 clean_attributes=True,
                                 run_start_hooks="all")
        self.obj1.db.damage = 1
        self.obj1.db.weight = 1.0
        self.obj1.db.range = 5
        # pick it up to wield the weapon
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('wield Obj')
        # test the at_equip hooks
        self.assertEqual(self.char1.traits.ATKR.actual, 4)
        self.assertEqual(self.char1.equip.get('wield1'), self.obj1)
        self.assertIs(self.char1.equip.get('wield2'), self.obj1)

    def test_wear(self):
        """test wear command"""
        # can't wear from the ground
        self.call(CmdWear(), 'Obj2', "You don't have 'Obj2' in your inventory.")
        # pick it up to wear armor
        self.char1.execute_cmd('get Obj2')
        self.call(CmdWear(), 'Obj2', "You wear Obj2(#5).")
        # check at_equip hooks ran
        self.assertEqual(self.char1.equip.get('armor'), self.obj2)
        # cannot wear a weapon
        self.char1.execute_cmd('get Obj')
        self.call(CmdWear(), 'Obj', "You can't wear Obj(#4).")

    def test_equip_list(self):
        """test the equip command"""
        self.call(CmdEquip(), "", "You have nothing in your equipment.")
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('wield Obj')
        self.char1.execute_cmd('get Obj2')
        self.char1.execute_cmd('wear Obj2')
        output = (
"Your equipment:\n"
"   Wield1: Obj                   (Damage:  1) (Melee)  \n"
"    Armor: Obj2                  (Toughness:  1)")
        self.call(CmdEquip(), "", output)
        self.char1.execute_cmd('drop Obj')
        self.call(CmdEquip(), "", "Your equipment:\n    Armor: Obj2                  (Toughness:  1)")

    def test_equip_item(self):
        """test equipping items with equip"""
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('get Obj2')
        self.call(CmdEquip(), "Obj", "You wield Obj(#4).")
        self.call(CmdEquip(), "Obj2", "You wear Obj2(#5).")

    def test_remove(self):
        """test the remove command"""
        self.call(CmdRemove(), "Obj", "You do not have 'Obj' equipped.")
        self.char1.execute_cmd('get Obj')
        self.char1.execute_cmd('wield Obj')
        self.call(CmdRemove(), "Obj", "You remove Obj(#4).")

    def test_inventory(self):
        """test the inventory command"""
        # empty inventory
        self.call(CmdInventory(), "", "You are not carrying anything.")
        # can see an object when picked up
        self.char1.execute_cmd('get Obj')
        self.call(CmdInventory(), "", "You are carrying:\n Obj  Test Obj  (Damage:  1) (Melee)")
        # but not when equipped
        self.char1.execute_cmd('wield Obj')
        self.call(CmdInventory(), "", "You are not carrying anything.")


class CharTraitsTestCase(CommandTest):
    """Character sheet and traits test case."""
    def setUp(self):
        self.character_typeclass = Character
        super(CharTraitsTestCase, self).setUp()
        apply_archetype(self.char1, 'warrior')
        self.char1.traits.STR.base += 3
        self.char1.traits.PER.base += 1
        self.char1.traits.DEX.base += 1
        self.char1.traits.VIT.base += 3
        calculate_secondary_traits(self.char1.traits)

    def test_sheet(self):
        """test character sheet display"""
        sheet_output = """==============[ Character Info ]===============o
                                                                               Name:                         Char     XP:     0 /       500   Level:   0    Archetype:                 Warrior                                                                                     HP   |   SP   |   BM   |   WM     Primary Traits  Strength    :    9    ~~~~~~~~+~~~~~~~~+~~~~~~~~+~~~~~~~~  ~~~~~~~~~~~~~~  Perception  :    2      9 / 9 |  9 / 9 |  0 / 0 |  0 / 0                   Intelligence:    1                                                         Dexterity   :    5    Race:                         None                   Charisma    :    4    Focus:                        None                   Vitality    :    9    Description                                          Magic       :    0    ~~~~~~~~~~~                          |  None                                 Save Rolls      Fortitude   :    9                                         ~~~~~~~~~~      Reflex      :    3                                                         Will        :    1    Encumbrance                          |  ~~~~~~~~~~~                          Combat Stats    Melee       :    9    Carry Weight:            0 /   180   ~~~~~~~~~~~~    Ranged      :    2    Encumbrance Penalty:             0   Power Point     Unarmed     :    5    Movement Points:                 5   Bonus:    +2    Defense     :    5                                         +"""

        self.call(CmdSheet(), "", sheet_output)

    def test_traits_no_args(self):
        self.call(CmdTraits(), "", "Usage: traits <traitgroup>")

    def test_primary_traits(self):
        expected = {
            "Strength": 9,
            "Perception": 2,
            "Intelligence": 1,
            "Dexterity": 5,
            "Charisma": 4,
            "Vitality": 9,
            "Magic": 0,
        }
        raw_output = self.call(CmdTraits(), "pri")
        parsed_output = _parse_to_dict(raw_output)
        self.assertDictEqual(expected, parsed_output)

    def test_secondary_traits(self):
        expected = {
            "Health": 9,
            "Black Mana": 0,
            "Stamina": 9,
            "White Mana": 0
        }
        raw_output = self.call(CmdTraits(), "secondary")
        parsed_output = _parse_to_dict(raw_output)
        self.assertDictEqual(expected, parsed_output)

    def test_save_rolls(self):
        expected = {
            "Fortitude Save": 9,
            "Reflex Save": 3,
            "Will Save": 1,
        }
        raw_output = self.call(CmdTraits(), "sav")
        parsed_output = _parse_to_dict(raw_output)
        self.assertDictEqual(expected, parsed_output)

    def test_combat_stats(self):
        expected = {
            "Melee Attack": 9,
            "Ranged Attack": 2,
            "Unarmed Attack": 5,
            "Defense": 5,
            "Power Points": 2
        }
        raw_output = self.call(CmdTraits(), "com")
        parsed_output = _parse_to_dict(raw_output)
        self.assertDictEqual(expected, parsed_output)


class BuildingTestCase(CommandTest):
    """Test case for Builder commands."""
    def setUp(self):
        self.character_typeclass = Character
        self.object_typeclass = NPC
        self.room_typeclass = Room
        super(BuildingTestCase, self).setUp()
        self.obj1.sdesc.add(self.obj1.key)

    def test_terrain_cmd(self):
        """test @terrain command"""
        # no args gives usage
        self.call(CmdTerrain(), "", "Usage: @terrain [<room>] = <terrain>")
        # equal sign only gives usage
        self.call(CmdTerrain(), "=", "Usage: @terrain [<room>] = <terrain>")
        # setting terrain on current room
        self.call(CmdTerrain(), "= DIFFICULT", "Terrain type 'DIFFICULT' set on Room.")
        self.assertEqual(self.room1.terrain, 'DIFFICULT')
        # terrain is case insensitive
        self.call(CmdTerrain(), "= vegetation", "Terrain type 'VEGETATION' set on Room.")
        self.assertEqual(self.room1.terrain, 'VEGETATION')
        # attempt with invalid terrain name
        self.call(CmdTerrain(), "= INVALID", "Invalid terrain type.")
        self.assertEqual(self.room1.terrain, 'VEGETATION')
        # setting terrain on a different room
        self.call(CmdTerrain(), "Room2 = QUICKSAND", "Terrain type 'QUICKSAND' set on Room2.")

    def test_rangefield_cmd(self):
        """test @rangefield command"""
        # no args
        self.call(CmdCapacity(), "", "Usage: @capacity [<room>] = <maxchars>")
        # equal sign only
        self.call(CmdCapacity(), "=", "Usage: @capacity [<room>] = <maxchars>")
        # nonnumeric
        self.call(CmdCapacity(), "= X", "Invalid capacity specified.")
        # negative
        self.call(CmdCapacity(), "= -23", "Invalid capacity specified.")
        # zero
        self.call(CmdCapacity(), "= 0", "Invalid capacity specified.")
        # success
        self.call(CmdCapacity(), "= 5", "Capacity set on Room(#1).")
        self.assertEqual(self.room1.db.max_chars, 5)
        # setting range field on a different room
        self.call(CmdCapacity(), "Room2 = 10", "Capacity set on Room2(#2).")
        self.assertEqual(self.room2.db.max_chars, 10)

    def test_settraits_cmd(self):
        """test @traits command"""
        # no args
        self.call(CmdSetTraits(), "", "Usage: @traits <npc> [trait[,trait..][ = value[,value..]]]")
        # display object's traits
        self.call(CmdSetTraits(), "Obj", "| Dexterity         :    1 | Black Mana        :    0 | Health            :    0 | Perception        :    1 | Action Points     :    0 | Defense           :    0 | Power Points      :    0 | Level             :    0 | White Mana        :    0 | Charisma          :    1 | Carry Weight      :    0 | Magic             :    0 | Reflex Save       :    0 | Strength          :    1 | Experience        :    0 | Fortitude Save    :    0 | Melee Attack      :    0 | Intelligence      :    1 | Stamina           :    0 | Will Save         :    0 | Movement Points   :    6 | Vitality          :    1 | Unarmed Attack    :    0 | Ranged Attack     :    0")
        # display specific named traits
        self.call(CmdSetTraits(), "Obj STR,BM,WM,INT,FORT", "| Strength          :    1 | Black Mana        :    0 | White Mana        :    0 | Intelligence      :    1 | Fortitude Save    :    0 |")
        # ignore invalid traits for display
        self.call(CmdSetTraits(), "Obj STR,INVALID", "| Strength          :    1")
        # assign a trait
        self.call(CmdSetTraits(), "Obj STR = 8", 'Trait "STR" set to 8 for Obj|\n| Strength          :    8')
        self.assertEqual(self.obj1.traits.STR.actual, 8)
        # ignore invalid traits in assignment
        self.call(CmdSetTraits(), "Obj STR,INVALID,PER = 7,5,6", 'Trait "STR" set to 7 for Obj|Invalid trait: "INVALID"|Trait "PER" set to 6 for Obj|\n| Strength          :    7 | Perception        :    6')
        self.assertEqual(self.obj1.traits.STR.actual, 7)
        self.assertEqual(self.obj1.traits.PER.actual, 6)
        # handle invalid arg combinations
        self.call(CmdSetTraits(), "Obj INVALID", "| Dexterity         :    1 | Black Mana        :    0 | Health            :    0 | Perception        :    6 | Action Points     :    0 | Defense           :    0 | Power Points      :    0 | Level             :    0 | White Mana        :    0 | Charisma          :    1 | Carry Weight      :    0 | Magic             :    0 | Reflex Save       :    0 | Strength          :    7 | Experience        :    0 | Fortitude Save    :    0 | Melee Attack      :    0 | Intelligence      :    1 | Stamina           :    0 | Will Save         :    0 | Movement Points   :    6 | Vitality          :    1 | Unarmed Attack    :    0 | Ranged Attack     :    0")
        self.call(CmdSetTraits(), "Obj STR, INT = 5, 6, 7", "Incorrect number of assignment values.")
        self.call(CmdSetTraits(), "Obj STR = X", "Assignment values must be numeric.")


class SetSkillTestCase(CommandTest):
    """Test case for Builder SetSkill command."""

    def setUp(self):
        self.character_typeclass = Character
        self.object_typeclass = NPC
        self.room_typeclass = Room
        super().setUp()
        self.obj1.sdesc.add(self.obj1.key)

    def test_without_args(self):
        self.call(CmdSetSkills(), "", "Usage: @skills <npc> [skill[,skill..][ = value[,value..]]]")

    def test_display_object_skills(self):
        self.call(CmdSetSkills(), "Obj", "Animal Handle     :    1 Appraise          :    1 Balance           :    1 Barter            :    1 Climb             :    1 Escape            :    1 Jump              :    1 Leadership        :    1 Listen            :    1 Lock Pick         :    1 Medicine          :    1 Sense Danger      :    1 Sneak             :    1 Survival          :    1 Throwing          :    1")

    def test_display_named_skills(self):
        self.call(CmdSetSkills(), "Obj escape,jump,medicine,survival", "Escape            :    1 Jump              :    1 Medicine          :    1 Survival          :    1")

    def test_ignore_invalid_skills_for_display(self):
        self.call(CmdSetSkills(), "Obj sense, notaskill", "Sense Danger      :    1")

    def test_assign_a_skill(self):
        self.call(CmdSetSkills(), "Obj jump = 4", 'Skill "jump" set to 4 for Obj|\nJump              :    4')
        self.assertEqual(self.obj1.skills.jump.actual, 4)

    def test_ignore_invalid_skills_in_assignment(self):
        self.call(CmdSetSkills(), "Obj barter,sneak,noskill = 3, 4, 10", 'Skill "barter" set to 3 for Obj|Skill "sneak" set to 4 for Obj|Invalid skill: "noskill"|\nBarter            :    3 Sneak             :    4')
        self.assertEqual(self.obj1.skills.barter.actual, 3)
        self.assertEqual(self.obj1.skills.sneak.actual, 4)

    def test_handle_invalid_arg_combinations(self):
        raw_output = self.call(CmdSetSkills(), "Obj INVALID")
        parsed_output = _parse_to_dict(raw_output)
        self.assertGreaterEqual(len(parsed_output), 1)
        self.call(CmdSetSkills(), "Obj leadership, animal = 2, 3, 2", "Incorrect number of assignment values.")
        self.call(CmdSetSkills(), "Obj escape = X", "Assignment values must be numeric.")


def _parse_to_dict(traits_output):
    """
    This is used to test for traits when the values are important
    and the order or display isn't.
    """
    groups = _TRAITS_MATCH_REGEX.findall(traits_output)
    traits = {}
    for match_str in groups:
        trait_name, value = match_str.split(":")
        stripped_trait_name = trait_name.strip()
        stripped_value = value.strip()
        if stripped_value.isdigit():
            traits[stripped_trait_name] = int(stripped_value)
        else:
            traits[stripped_trait_name] = stripped_value

    return traits
