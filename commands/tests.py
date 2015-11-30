# A trivial test for Travis

from evennia.commands.default.tests import CommandTest
from commands.equip_commands import CmdEquip
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
"YPrimary Traitsn|\n"
" CStrength         n : w  9n  CPerception       n : w  2n  CIntelligence     n : w  1n \n"
" CDexterity        n : w  5n  CCharisma         n : w  4n  CVitality         n : w  9n \n"
" CMagic            n : w  0n  C                 n : w   n  C                 n : w   n \n")
        self.call(CmdTraits(), "pri", output)
        # test secondary traits
        output = (
"YSecondary Traitsn|\n"
" CHealth                        n : w  9n  CBlack Mana                    n : w  0n \n"
" CStamina                       n : w  9n  CWhite Mana                    n : w  0n \n")
        self.call(CmdTraits(), "secondary", output)
        # test save rolls
        output = (
"YSave Rollsn|\n"
" CFortitude Save   n : w  9n  CReflex Save      n : w  5n  CWill Save        n : w  1n \n")
        self.call(CmdTraits(), "sav", output)
        # test combat stats
        output = (
"YCombat Statsn|\n"
" CMelee Attack     n : w  9n  CRanged Attack    n : w  2n  CUnarmed Attack   n : w  5n \n"
" CDefense          n : w  5n  CPower Points     n : w  2n  C                 n : w   n \n")
        self.call(CmdTraits(), "com", output)
