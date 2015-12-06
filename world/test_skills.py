"""
Skills test module.
"""

from django.test import TestCase
from evennia.utils.test_resources import EvenniaTest
from typeclasses.characters import Character
from world import skills, archetypes


class LoadSkillTestCase(TestCase):
    """Test case for the `load_skill` module function."""
    def test_escape(self):
        """test that Escape skill loads correctly"""
        s = skills.load_skill('escape')
        self.assertEqual(s.name, 'Escape')
        self.assertEqual(s.base, 'STR')

    def test_climb(self):
        """test that Climb skill loads correctly"""
        s = skills.load_skill('climb')
        self.assertEqual(s.name, 'Climb')
        self.assertEqual(s.base, 'STR')

    def test_jump(self):
        """test that Jump skill loads correctly"""
        s = skills.load_skill('jump')
        self.assertEqual(s.name, 'Jump')
        self.assertEqual(s.base, 'STR')

    def test_lockpick(self):
        """test that Lock Pick skill loads correctly"""
        s = skills.load_skill('lockpick')
        self.assertEqual(s.name, 'Lock Pick')
        self.assertEqual(s.base, 'PER')

    def test_lockpick(self):
        """test that Listen skill loads correctly"""
        s = skills.load_skill('listen')
        self.assertEqual(s.name, 'Listen')
        self.assertEqual(s.base, 'PER')

    def test_sense(self):
        """test that Sense Danger skill loads correctly"""
        s = skills.load_skill('sense')
        self.assertEqual(s.name, 'Sense Danger')
        self.assertEqual(s.base, 'PER')

    def test_appraise(self):
        """test that Appraise skill loads correctly"""
        s = skills.load_skill('appraise')
        self.assertEqual(s.name, 'Appraise')
        self.assertEqual(s.base, 'INT')

    def test_medicine(self):
        """test that Medicine skill loads correctly"""
        s = skills.load_skill('medicine')
        self.assertEqual(s.name, 'Medicine')
        self.assertEqual(s.base, 'INT')

    def test_survival(self):
        """test that Survival skill loads correctly"""
        s = skills.load_skill('survival')
        self.assertEqual(s.name, 'Survival')
        self.assertEqual(s.base, 'INT')

    def test_balance(self):
        """test that Balance skill loads correctly"""
        s = skills.load_skill('balance')
        self.assertEqual(s.name, 'Balance')
        self.assertEqual(s.base, 'DEX')

    def test_sneak(self):
        """test that Sneak skill loads correctly"""
        s = skills.load_skill('sneak')
        self.assertEqual(s.name, 'Sneak')
        self.assertEqual(s.base, 'DEX')

    def test_throwing(self):
        """test that Throwing skill loads correctly"""
        s = skills.load_skill('throwing')
        self.assertEqual(s.name, 'Throwing')
        self.assertEqual(s.base, 'DEX')

    def test_animal(self):
        """test that Animal Handle skill loads correctly"""
        s = skills.load_skill('animal')
        self.assertEqual(s.name, 'Animal Handle')
        self.assertEqual(s.base, 'CHA')

    def test_barter(self):
        """test that Barter skill loads correctly"""
        s = skills.load_skill('barter')
        self.assertEqual(s.name, 'Barter')
        self.assertEqual(s.base, 'CHA')

    def test_leadership(self):
        """test that Leadership skill loads correctly"""
        s = skills.load_skill('leadership')
        self.assertEqual(s.name, 'Leadership')
        self.assertEqual(s.base, 'CHA')


class CharSkillsTestCase(EvenniaTest):
    """Test case for module functions that operate on characters."""
    def setUp(self):
        self.character_typeclass = Character
        super(CharSkillsTestCase, self).setUp()
        archetypes.apply_archetype(self.char1, 'warrior')
        tr = self.char1.traits
        tr.STR.base += 2
        tr.PER.base += 1
        tr.INT.base += 1
        tr.DEX.base += 1
        tr.CHA.base += 1
        tr.VIT.base += 2

    def test_apply_skills(self):
        """test module function `apply_skills`"""
        skills.apply_skills(self.char1)
        sk = self.char1.skills
        self.assertEqual(sk.escape.actual, 8)
        self.assertEqual(sk.climb.actual, 8)
        self.assertEqual(sk.jump.actual, 8)
        self.assertEqual(sk.lockpick.actual, 2)
        self.assertEqual(sk.listen.actual, 2)
        self.assertEqual(sk.sense.actual, 2)
        self.assertEqual(sk.appraise.actual, 2)
        self.assertEqual(sk.medicine.actual, 2)
        self.assertEqual(sk.survival.actual, 2)
        self.assertEqual(sk.balance.actual, 5)
        self.assertEqual(sk.sneak.actual, 5)
        self.assertEqual(sk.throwing.actual, 5)
        self.assertEqual(sk.animal.actual, 5)
        self.assertEqual(sk.barter.actual, 5)
        self.assertEqual(sk.leadership.actual, 5)

    def test_validate_skills(self):
        """test module function `apply_skills`"""
        skills.apply_skills(self.char1)
        # not
        self.assertFalse(skills.validate_skills(self.char1)[0])
        self.assertIn('Not enough -1',
                      skills.validate_skills(self.char1)[1])
        sk = self.char1.skills
        sk.escape.minus += 1
        sk.climb.minus += 1
        sk.jump.minus += 1
        sk.medicine.plus += 1
        self.assertTrue(skills.validate_skills(self.char1)[0])
        sk.appraise.plus += 1
        self.assertFalse(skills.validate_skills(self.char1)[0])
        self.assertIn('Not enough +1',
                      skills.validate_skills(self.char1)[1])

    def test_finalize_skills(self):
        """test module function `finalize_skills`"""
        skills.apply_skills(self.char1)
        # allocate skills for char1
        sk = self.char1.skills
        sk.escape.minus += 1
        sk.climb.minus += 1
        sk.jump.minus += 1
        sk.medicine.plus += 1
        skills.finalize_skills(sk)
        # confirm the plusses and minuses are applied
        self.assertEqual(sk.escape.actual, 7)
        self.assertEqual(sk.climb.actual, 7)
        self.assertEqual(sk.jump.actual, 7)
        self.assertEqual(sk.medicine.actual, 3)
        # confirm plus/minus counters are deleted
        with self.assertRaises(AttributeError):
            x = sk.escape.plus
        with self.assertRaises(AttributeError):
            x = sk.escape.minus
