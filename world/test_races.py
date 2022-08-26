"""
Unit tests for the races module.
"""

from django.test import TestCase
from evennia.utils.test_resources import EvenniaTest
from typeclasses.characters import Character
from world.archetypes import apply_archetype, calculate_secondary_traits
from world import races


class RacesTestCase(TestCase):
    """Test case for Race classes."""
    def test_load_human(self):
        """test that `load_race` loads Human race class"""
        h = races.load_race('human')
        self.assertEqual(h.name, 'Human')
        self.assertEqual(h.plural, 'Humans')
        self.assertEqual(h.size, 'medium')
        self.assertIn(h.foci[0].name, ('Agility', 'Cunning', 'Prestige'))
        self.assertIn(h.foci[1].name, ('Agility', 'Cunning', 'Prestige'))
        self.assertIn(h.foci[2].name, ('Agility', 'Cunning', 'Prestige'))
        self.assertEqual(h.bonuses, {'WILL': 1})

    def test_load_elf(self):
        """test that `load_race` loads Elf race class"""
        e = races.load_race('elf')
        self.assertEqual(e.name, 'Elf')
        self.assertEqual(e.plural, 'Elves')
        self.assertEqual(e.size, 'medium')
        self.assertIn(e.foci[0].name, ('Agility', 'Spirit', 'Alertness'))
        self.assertIn(e.foci[1].name, ('Agility', 'Spirit', 'Alertness'))
        self.assertIn(e.foci[2].name, ('Agility', 'Spirit', 'Alertness'))
        self.assertEqual(e.bonuses, {})

    def test_load_dwarf(self):
        """test that `load_race` loads Dwarf race class"""
        e = races.load_race('dwarf')
        self.assertEqual(e.name, 'Dwarf')
        self.assertEqual(e.plural, 'Dwarves')
        self.assertEqual(e.size, 'small')
        self.assertIn(e.foci[0].name, ('Brawn', 'Resilience', 'Alertness'))
        self.assertIn(e.foci[1].name, ('Brawn', 'Resilience', 'Alertness'))
        self.assertIn(e.foci[2].name, ('Brawn', 'Resilience', 'Alertness'))
        self.assertEqual(e.bonuses, {'WILL': 1})


class FocusTestCase(TestCase):
    """Test case for Focus classes."""
    def test_load_focus(self):
        """test that `load_focus` loads the correct Focus instance"""
        f = races.load_focus('agility')
        self.assertEqual(f.name, 'Agility')
        self.assertDictEqual(f.bonuses, {'STR': 1, 'DEX': 2, 'REFL': 2})
        f = races.load_focus('alertness')
        self.assertEqual(f.name, 'Alertness')
        self.assertDictEqual(f.bonuses, {'PER': 2, 'CHA': 1, 'REFL': 2})
        f = races.load_focus('brawn')
        self.assertEqual(f.name, 'Brawn')
        self.assertDictEqual(f.bonuses, {'STR': 2, 'VIT': 1, 'FORT': 1})
        f = races.load_focus('cunning')
        self.assertEqual(f.name, 'Cunning')
        self.assertDictEqual(f.bonuses, {'PER': 1, 'INT': 2, 'WILL': 3})
        f = races.load_focus('prestige')
        self.assertEqual(f.name, 'Prestige')
        self.assertDictEqual(f.bonuses, {'INT': 1, 'CHA': 2})
        f = races.load_focus('resilience')
        self.assertEqual(f.name, 'Resilience')
        self.assertDictEqual(f.bonuses,
                             {'DEX': 1, 'VIT': 2, 'FORT': 3, 'WILL': 2})
        f = races.load_focus('spirit')
        self.assertEqual(f.name, 'Spirit')
        self.assertDictEqual(
            f.bonuses,
            {'VIT': 1, 'MAG': 2, 'FORT': 1, 'REFL': 1, 'WILL': 1})


class ApplyRaceTestCase(EvenniaTest):
    """Test case for applying race to a character."""
    def setUp(self):
        self.character_typeclass = Character
        super(ApplyRaceTestCase, self).setUp()
        # make sure char1 has traits to give bonuses to
        apply_archetype(self.char1, 'warrior')
        self.char1.traits.STR.base += 2
        self.char1.traits.PER.base += 1
        self.char1.traits.INT.base += 1
        self.char1.traits.DEX.base += 1
        self.char1.traits.CHA.base += 1
        self.char1.traits.VIT.base += 2
        calculate_secondary_traits(self.char1.traits)

    def check_traits(self, str, per, int, dex, cha, vit, mag, fort, refl, will):
        """enables one-line check of all character traits"""
        self.assertEqual(self.char1.traits.STR.value, str)
        self.assertEqual(self.char1.traits.PER.value, per)
        self.assertEqual(self.char1.traits.INT.value, int)
        self.assertEqual(self.char1.traits.DEX.value, dex)
        self.assertEqual(self.char1.traits.CHA.value, cha)
        self.assertEqual(self.char1.traits.VIT.value, vit)
        self.assertEqual(self.char1.traits.MAG.value, mag)
        self.assertEqual(self.char1.traits.FORT.value, fort)
        self.assertEqual(self.char1.traits.REFL.value, refl)
        self.assertEqual(self.char1.traits.WILL.value, will)

    def test_apply_human_agility(self):
        """test character becoming human with agility focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'human', 'agility')
        # human/agility bonuses: 1 will, 1 str, 2 dex, 2 refl
        self.check_traits(9, 2, 2, 7, 5, 8, 0, 8, 5, 3)

    def test_apply_human_cunning(self):
        """test character becoming human with cunning focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'human', 'cunning')
        # human/cunning bonuses: 4 will, 1 per, 2 int
        self.check_traits(8, 3, 4, 5, 5, 8, 0, 8, 3, 6)

    def test_apply_human_prestige(self):
        """test character becoming human with prestige focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'human', 'prestige')
        # human/prestige bonuses: 1 will, 1 int, 2 cha
        self.check_traits(8, 2, 3, 5, 7, 8, 0, 8, 3, 3)

    def test_apply_elf_agility(self):
        """test character becoming elf with agility focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'elf', 'agility')
        # elf/agility bonuses: 1 str, 2 dex, 2 refl
        self.check_traits(9, 2, 2, 7, 5, 8, 0, 8, 5, 2)

    def test_apply_elf_spirit(self):
        """test character becoming elf with spirit focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'elf', 'spirit')
        # elf/spirit bonuses: 1 vit, 2 mag, 1 fort, 1 refl, 1 will
        self.check_traits(8, 2, 2, 5, 5, 9, 2, 9, 4, 3)

    def test_apply_elf_alertness(self):
        """test character becoming elf with alertness focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'elf', 'alertness')
        # elf/alertness bonuses: 2 per, 1 cha, 2 refl
        self.check_traits(8, 4, 2, 5, 6, 8, 0, 8, 5, 2)

    def test_apply_dwarf_brawn(self):
        """test character becoming dwarf with brawn focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'dwarf', 'brawn')
        # dwarf/brawn bonuses: 2 str, 1 vit, 1 fort, 1 will
        self.check_traits(10, 2, 2, 5, 5, 9, 0, 9, 3, 3)

    def test_apply_dwarf_resilience(self):
        """test character becoming dwarf with resilience focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'dwarf', 'resilience')
        # dwarf/resilience bonuses: 1 dex, 2 vit, 3 fort, 3 will
        self.check_traits(8, 2, 2, 6, 5, 10, 0, 11, 3, 5)

    def test_apply_dwarf_alertness(self):
        """test character becoming dwarf with alertness focus"""
        self.check_traits(8, 2, 2, 5, 5, 8, 0, 8, 3, 2)
        races.apply_race(self.char1, 'dwarf', 'alertness')
        # dwarf/alertness bonuses: 2 per, 1 cha, 2 refl, 1 will
        self.check_traits(8, 4, 2, 5, 6, 8, 0, 8, 5, 3)
