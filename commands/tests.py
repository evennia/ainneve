# A trivial test for Travis

from evennia.commands.default.tests import CommandTest
from commands.equip import CmdEquip
from typeclasses.characters import Character

class TestEquip(CommandTest):
    character_typeclass = Character
    def test_equip(self):
        self.call(CmdEquip(), "", "You have nothing in your equipment.")


from commands.chartraits import CmdSheet, CmdTraits
from world.archetypes import apply_archetype, calculate_secondary_traits


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
        sheet_output = (
"==============[ Character Info ]===============\n" + (77 * " ") + "\n"
"  Name:                         Char     XP:     0 /       500   Level:   0  \n"
"  Archetype:                 Warrior                                         \n"
+ (39 * " ") + "\n"
"     HP      SP      BM      WM      Primary Traits   Strength    :   9  \n"
"  ~~~~~~~~+~~~~~~~~+~~~~~~~~+~~~~~~~~   ~~~~~~~~~~~~~~   Perception  :   2  \n"
"    9 / 9   9 / 9   0 / 0   0 / 0                     Intelligence:   1  \n"
"                                                         Dexterity   :   5  \n"
"  Race:                         None                     Charisma    :   4  \n"
"  Focus:                        None                     Vitality    :   9  \n"
"  Description                                            Magic       :   0  \n"
"  ~~~~~~~~~~~                            \n"
"  None                                  Save Rolls       Fortitude   :   9  \n"
"                                        ~~~~~~~~~~       Reflex      :   5  \n"
"                                                         Will        :   1  \n"
"  Encumbrance                            \n"
"  ~~~~~~~~~~~                           Combat Stats     Melee       :   9  \n"
"  Carry Weight:             0 /  180    ~~~~~~~~~~~~     Ranged      :   2  \n"
"  Encumbrance Penalty:             0    Power Point      Unarmed     :   5  \n"
"  Movement Points:                 5    Bonus:    +2     Defense     :   5")
        self.call(CmdSheet(), "", sheet_output)

    def test_traits(self):
        """test traits command"""
        # test no args
        self.call(CmdTraits(), "", "Usage: traits <traitgroup>")
        # test primary traits
        output = (
"[ Primary Traits ]|\n"
" Strength      9 \n"
" Perception    2 \n"
" Intelligence  1 \n"
" Dexterity     5 \n"
" Charisma      4 \n"
" Vitality      9 \n"
" Magic         0")
        self.call(CmdTraits(), "pri", output)
        # test secondary traits
        output = (
"[ Secondary Traits ]|\n"
" Health      9 \n"
" Stamina     9 \n"
" Black Mana  0 \n"
" White Mana  0")
        self.call(CmdTraits(), "secondary", output)
        # test save rolls
        output = (
"[ Save Rolls ]|\n"
" Fortitude Save  9 \n"
" Reflex Save     5 \n"
" Will Save       1")
        self.call(CmdTraits(), "sav", output)
        # test combat stats
        output = (
"[ Combat Stats ]|\n"
" Melee Attack    9 \n"
" Ranged Attack   2 \n"
" Unarmed Attack  5 \n"
" Defense         5 \n"
" Power Points    2")
        self.call(CmdTraits(), "com", output)
