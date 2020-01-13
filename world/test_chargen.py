"""
Character generation test module.
"""
from django.conf import settings
from evennia.utils import ansi
from evennia.utils.evmenu import EvMenu
from evennia.utils.test_resources import EvenniaTest
from mock import Mock

from server.conf.settings import PROTOTYPE_MODULES
from typeclasses.characters import Character
from world.chargen import *


class ChargenTestCase(EvenniaTest):
    """Test case for the chargen menu process."""
    character_typeclass = Character

    def setUp(self):
        super(ChargenTestCase, self).setUp()
        self.session.msg = Mock()
        settings.PROTOTYPE_MODULES = PROTOTYPE_MODULES

    def test_launch_chargen(self):
        """test launching the chargen menu"""
        self.session.execute_cmd('@charcreate TestChar')
        self.assertIsInstance(self.session.ndb._menutree, EvMenu)
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u'|n|wWelcome to |mAinneve|w, the example game for |yEvennia|w.|n',
                      msg.split('\n'))

    def test_launch_existing_start(self):
        """test chargen on existing character; no archetype assigned"""
        self.session.execute_cmd('@charcreate Char')
        self.assertIsInstance(self.session.ndb._menutree, EvMenu)
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u'|n|wWelcome to |mAinneve|w, the example game for |yEvennia|w.|n',
                      msg.split('\n'))

    def test_launch_existing_archetype(self):
        """test chargen on existing character; archetype assigned"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.session.execute_cmd('@charcreate Char')
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"|nYour character's traits influence combat abilities and skills.",
                      msg.split('\n'))

    def test_launch_existing_traits(self):
        """test chargen on existing character; traits allocated"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.char1.traits.INT.base += 8
        self.session.execute_cmd('@charcreate Char')
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"|nNext, select a race for your character:|n",
                      msg.split('\n'))

    def test_launch_existing_race_magic(self):
        """test chargen on existing character; race assigned; magic"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.char1.traits.MAG.base += 8
        races.apply_race(self.char1, 'human', 'agility')
        self.session.execute_cmd('@charcreate Char')
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"|nYour |CMagic|n trait is |w8|n.",
                      msg.split('\n'))

    def test_launch_existing_race_nomagic(self):
        """test chargen on existing character; race assigned; no magic"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.char1.traits.INT.base += 8
        races.apply_race(self.char1, 'human', 'agility')
        self.session.execute_cmd('@charcreate Char')
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"|nYour ability to perform actions in Ainneve is",
                      msg.split('\n'))

    def test_launch_existing_unallocated_skills(self):
        """test chargen on existing character; skills not fully allocated"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.char1.traits.INT.base += 8
        races.apply_race(self.char1, 'human', 'agility')
        skills.apply_skills(self.char1)
        self.session.execute_cmd('@charcreate Char')
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"|nYour ability to perform actions in Ainneve is",
                      msg.split('\n'))

    def test_launch_existing_skills_allocated(self):
        """test chargen on existing character; skills allocated"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.char1.traits.INT.base += 8
        races.apply_race(self.char1, 'human', 'agility')
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        self.session.execute_cmd('@charcreate Char')
        # this menu node returns the chars inventory then menu text
        # so we use mock_calls[1] instead of 0
        msg = self.session.msg.mock_calls[0][1][0]
        self.assertIn(u"Select a category of equipment to view:|n",
                      msg.split('\n'))

    def test_ic_character(self):
        """test chargen overridden @ic command"""
        self.session.execute_cmd('@ic Char')
        # confirm the menu displayed the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Select an Archetype by number', last_msg)

    def test_node_welcome(self):
        """test welcome node output"""
        self.session.new_char = self.char1
        (text, help), options = menunode_welcome_archetypes(self.session)
        opt_texts = [ansi.strip_ansi(o['desc']) for o in options]
        self.assertEqual(opt_texts, ['Arcanist', 'Scout', 'Warrior',
                                     'Warrior-Scout', 'Warrior-Arcanist',
                                     'Arcanist-Scout'])

    def test_node_select_archetype_padded(self):
        """make sure that entries with leading/trailing spaces are handled"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd(' 1')
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Arcanist', last_msg)
        self.session.execute_cmd('N')
        self.session.execute_cmd('1 ')
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Arcanist', last_msg)

    def test_node_select_arcanist(self):
        """test Arcanist archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('1')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Arcanist')

    def test_node_select_scout(self):
        """test Scout archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('2')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Scout')

    def test_node_select_warrior(self):
        """test Warrior archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('3')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Warrior')

    def test_node_select_warrior_scout(self):
        """test Warrior-Scout archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('4')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Scout')

    def test_node_select_warrior_arcanist(self):
        """test Warrior-Arcanist archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('5')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Arcanist')

    def test_node_select_arcanist_scout(self):
        """test Arcanist-Scout archetype selection via menu"""
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('6')
        self.session.execute_cmd('Y')
        self.assertEqual(self.char1.db.archetype, 'Arcanist-Scout')

    def test_node_allocate_traits(self):
        """test trait allocation node"""
        archetypes.apply_archetype(self.char1, 'scout')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(5)):
            self.session.execute_cmd('6')
        self.session.execute_cmd('5')
        self.session.execute_cmd('4 ')
        self.session.execute_cmd(' 3')
        self.assertEqual(self.char1.traits.STR.actual, 4)
        self.assertEqual(self.char1.traits.PER.actual, 6)
        self.assertEqual(self.char1.traits.INT.actual, 7)
        self.assertEqual(self.char1.traits.DEX.actual, 5)
        self.assertEqual(self.char1.traits.CHA.actual, 2)
        self.assertEqual(self.char1.traits.VIT.actual, 6)
        # confirm the menu displayed the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Next, select a race for your character:', last_msg)

    def test_node_allocate_traits_toomany(self):
        """test trait allocation node"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(5)):
            self.session.execute_cmd('1')
        self.assertEqual(self.char1.traits.STR.actual, 10)
        # confirm error message
        last_msg = ansi.strip_ansi(self.session.msg.mock_calls[-1][1][0])
        self.assertIn('Cannot allocate more than 10 points to one trait!', last_msg)

    def test_node_allocate_traits_startover(self):
        """test starting over after having allocated some traits"""
        archetypes.apply_archetype(self.char1, 'scout')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(5)):
            self.session.execute_cmd('6')
        self.session.execute_cmd('5')
        self.session.execute_cmd('4')
        self.session.execute_cmd('8')
        self.assertEqual(self.char1.traits.STR.actual, 4)
        self.assertEqual(self.char1.traits.PER.actual, 6)
        self.assertEqual(self.char1.traits.INT.actual, 6)
        self.assertEqual(self.char1.traits.DEX.actual, 4)
        self.assertEqual(self.char1.traits.CHA.actual, 1)
        self.assertEqual(self.char1.traits.VIT.actual, 1)
        # confirm the menu is still at trait allocation
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Allocate additional trait points as you choose.', last_msg)

    def test_node_select_human_agility(self):
        """test race/focus selection - human/agility"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd(' 1')
        self.session.execute_cmd(' 1')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Human')
        self.assertEqual(self.char1.db.focus, 'Agility')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_human_cunning(self):
        """test race/focus selection - human/cunning"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('1 ')
        self.session.execute_cmd('2 ')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Human')
        self.assertEqual(self.char1.db.focus, 'Cunning')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_human_prestige(self):
        """test race/focus selection - human/prestige"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('1')
        self.session.execute_cmd('3')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Human')
        self.assertEqual(self.char1.db.focus, 'Prestige')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_elf_agility(self):
        """test race/focus selection - elf/agility"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('2')
        self.session.execute_cmd('1')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Elf')
        self.assertEqual(self.char1.db.focus, 'Agility')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_elf_spirit(self):
        """test race/focus selection - elf/spirit"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('2')
        self.session.execute_cmd('2')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Elf')
        self.assertEqual(self.char1.db.focus, 'Spirit')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Select a mana counter to increase:', last_msg)

    def test_node_select_elf_alertness(self):
        """test race/focus selection - elf/alertness"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('2')
        self.session.execute_cmd('3')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Elf')
        self.assertEqual(self.char1.db.focus, 'Alertness')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_dwarf_brawn(self):
        """test race/focus selection - dwarf/brawn"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('3')
        self.session.execute_cmd('1')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Dwarf')
        self.assertEqual(self.char1.db.focus, 'Brawn')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_dwarf_resilience(self):
        """test race/focus selection - dwarf/resilience"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('3')
        self.session.execute_cmd('2')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Dwarf')
        self.assertEqual(self.char1.db.focus, 'Resilience')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_dwarf_alertness(self):
        """test race/focus selection - dwarf/alertness"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('3')
        self.session.execute_cmd('3')
        self.session.execute_cmd('yes')
        self.assertEqual(self.char1.db.race, 'Dwarf')
        self.assertEqual(self.char1.db.focus, 'Alertness')
        # confirm the menu is at the next node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_select_race_goback(self):
        """test the back/no functionality of the race/focus nodes"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('1')
        self.session.execute_cmd('Back')
        # confirm return to race selection screen
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Next, select a race for your character:', last_msg)
        # next go to focus confirmation and back up
        self.session.execute_cmd('1')
        self.session.execute_cmd('1')
        self.session.execute_cmd('No')
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Select a focus below to continue:', last_msg)
        self.session.execute_cmd('Back')
        # confirm return to race selection screen
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Next, select a race for your character:', last_msg)

    def test_node_mana_two_types(self):
        """test mana allocation node - two types"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        traits = self.char1.traits
        traits.VIT.mod = 3
        traits.DEX.mod = 2
        traits.INT.mod = traits.MAG.mod = 1
        races.apply_race(self.char1, 'elf', 'spirit')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(4)):
            self.session.execute_cmd(' 1')
        for i in list(range(5)):
            self.session.execute_cmd('2 ')
        self.assertEqual(traits.WM.base, 4)
        self.assertEqual(traits.BM.base, 5)
        self.assertEqual(traits.WM.max, 10)
        self.assertEqual(traits.BM.max, 10)
        # confirm return to race selection screen
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_mana_one_type(self):
        """test mana allocation node - one type"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        traits = self.char1.traits
        traits.VIT.mod = 3
        traits.DEX.mod = 2
        traits.INT.mod = traits.MAG.mod = 1
        races.apply_race(self.char1, 'elf', 'spirit')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(9)):
            self.session.execute_cmd('2')
        self.assertEqual(traits.WM.base, 0)
        self.assertEqual(traits.BM.base, 9)
        self.assertEqual(traits.WM.max, 0)
        self.assertEqual(traits.BM.max, 10)
        # confirm return to race selection screen
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('your character\'s skills.', last_msg)

    def test_node_mana_start_over(self):
        """test allocating some mana points, then starting over"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        traits = self.char1.traits
        traits.VIT.mod = 3
        traits.DEX.mod = 2
        traits.INT.mod = traits.MAG.mod = 1
        races.apply_race(self.char1, 'elf', 'spirit')
        self.session.execute_cmd('@charcreate Char')
        for i in list(range(4)):
            self.session.execute_cmd('1')
            self.session.execute_cmd('2')
        self.session.execute_cmd('3')
        self.assertEqual(traits.WM.base, 0)
        self.assertEqual(traits.BM.base, 0)
        self.assertEqual(traits.WM.max, 10)
        self.assertEqual(traits.BM.max, 10)
        # confirm return to race selection screen
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Select a mana counter to increase:', last_msg)

    def test_node_allocate_skills(self):
        """test skill allocation node"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        self.session.execute_cmd('@charcreate Char')
        # -1's
        self.session.execute_cmd(' 5')  # Listen
        self.session.execute_cmd('7 ')  # Appraise
        self.session.execute_cmd('9')   # Survival
        # +1's
        self.session.execute_cmd('1')   # Escape
        self.session.execute_cmd('13')  # Animal Handle
        self.session.execute_cmd('13')
        sk = self.char1.skills
        self.assertEqual(sk.escape.actual, 5)
        self.assertEqual(sk.climb.actual, 4)
        self.assertEqual(sk.jump.actual, 4)
        self.assertEqual(sk.lockpick.actual, 7)
        self.assertEqual(sk.listen.actual, 6)
        self.assertEqual(sk.sense.actual, 7)
        self.assertEqual(sk.appraise.actual, 8)
        self.assertEqual(sk.medicine.actual, 9)
        self.assertEqual(sk.survival.actual, 8)
        self.assertEqual(sk.balance.actual, 5)
        self.assertEqual(sk.sneak.actual, 5)
        self.assertEqual(sk.throwing.actual, 5)
        self.assertEqual(sk.animal.actual, 4)
        self.assertEqual(sk.barter.actual, 2)
        self.assertEqual(sk.leadership.actual, 2)
        # confirm we're on the equipment node
        last_msg = self.session.msg.mock_calls[-1][1][0]
        self.assertIn('Select a category of equipment to view:', last_msg)

    def test_node_allocate_skills_below_one(self):
        """test invalid skill allocation below 1"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('15')
        self.session.execute_cmd('15')
        self.assertEqual(self.char1.skills.leadership.minus, 1)
        # confirm error message
        last_msg = ansi.strip_ansi(self.session.msg.mock_calls[-1][1][0])
        self.assertIn('Skills cannot be reduced below one.', last_msg)
        self.assertIn("Please allocate two '-1' counters.", last_msg)

    def test_node_allocate_skills_above_ten(self):
        """test invalid skill allocation above 10"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        traits = self.char1.traits
        traits.VIT.mod = 2
        traits.DEX.mod = 2
        traits.INT.mod = 3
        traits.BM.base = 8
        races.apply_race(self.char1, 'elf', 'spirit')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        self.session.execute_cmd('@charcreate Char')
        # -1's
        self.session.execute_cmd('9')
        self.session.execute_cmd('9')
        self.session.execute_cmd('9')
        # +1's
        self.session.execute_cmd('7')
        self.session.execute_cmd('7')
        self.assertEqual(self.char1.skills.appraise.plus, 1)
        # confirm error message
        last_msg = ansi.strip_ansi(self.session.msg.mock_calls[-1][1][0])
        self.assertIn('Skills cannot be increased above ten.', last_msg)
        self.assertIn("Please allocate two '+1' counters.", last_msg)

    def test_node_allocate_skills_startover(self):
        """test starting over after allocating some skill counters"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        self.session.execute_cmd('@charcreate Char')
        # -1's
        self.session.execute_cmd('7')
        self.session.execute_cmd('8')
        self.session.execute_cmd('9')
        # +1's
        self.session.execute_cmd('4')
        self.session.execute_cmd('5')
        # start over
        self.session.execute_cmd('16')
        sk = self.char1.skills
        for s in sk.all:
            self.assertEqual(sk[s].minus, 0)
            self.assertEqual(sk[s].plus, 0)
        # confirm error message
        last_msg = ansi.strip_ansi(self.session.msg.mock_calls[-1][1][0])
        self.assertIn("Please allocate three '-1' counters.", last_msg)

    def test_node_equip_purchase(self):
        """test equipment 'purchasing' nodes"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        self.char1.db.wallet['SC'] = 10
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd(' 1 ')
        self.session.execute_cmd(' 12 ')
        self.session.execute_cmd('y')
        self.assertDictEqual({'GC': 0, 'SC': 9, 'CC': 70},
                             dict(self.char1.db.wallet))
        self.assertIn('a whip', [i.key for i in self.char1.contents])

    def test_node_equip_insuff_funds(self):
        """test insufficient funds messaging"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        # check insufficient funds
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('4')
        self.session.execute_cmd('3')
        self.session.execute_cmd('y')
        messages = [ansi.strip_ansi(args[0]) for n, args, kw
                    in self.session.msg.mock_calls]
        self.assertIn("You do not have enough money to buy a brigandine.", messages)

    def test_node_description(self):
        """test character description node"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('done')
        self.session.execute_cmd('test sdesc')
        self.session.execute_cmd('test description')
        self.assertEqual(self.char1.sdesc.get(), 'test sdesc')
        self.assertEqual(self.char1.db.desc, 'test description')

    def test_node_start_over(self):
        """test confirmation/start over node"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('done')
        self.session.execute_cmd('test sdesc')
        self.session.execute_cmd('test description')
        self.session.execute_cmd('no')

        self.assertEqual(len(self.char1.traits.all), 0)
        self.assertEqual(len(self.char1.skills.all), 0)
        self.assertEqual(len(self.char1.contents), 0)
        self.assertIsNone(self.char1.db.archetype)
        self.assertIsNone(self.char1.db.race)
        self.assertIsNone(self.char1.db.focus)
        self.assertEqual(self.char1.sdesc.get(), 'a normal person')
        self.assertIsNone(self.char1.db.desc)
        self.assertDictEqual(dict(self.char1.db.wallet),
                             {'GC': 0, 'SC': 0, 'CC': 0})

    def test_node_end(self):
        """confirm char.db.chargen_complete flag gets set"""
        archetypes.apply_archetype(self.char1, 'scout')
        traits = self.char1.traits
        traits.INT.mod = traits.DEX.mod = traits.CHA.mod = 1
        traits.VIT.mod = 5
        races.apply_race(self.char1, 'human', 'cunning')
        archetypes.calculate_secondary_traits(self.char1.traits)
        archetypes.finalize_traits(self.char1.traits)
        skills.apply_skills(self.char1)
        skills.finalize_skills(self.char1.skills)
        self.session.execute_cmd('@charcreate Char')
        self.session.execute_cmd('done')
        self.session.execute_cmd('test sdesc')
        self.session.execute_cmd('test description')
        self.session.execute_cmd('y')
        self.assertTrue(self.char1.db.chargen_complete)
