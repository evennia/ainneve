"""
Unit tests for world.archetypes module.
"""

from world import archetypes
from typeclasses.characters import Character
from evennia.utils.test_resources import EvenniaTest


class ArchetypeTestCase(EvenniaTest):
    """Test case for Archetype classes."""
    character_typeclass = Character

    def test_apply_warrior(self):
        """confirm the Warrior archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'warrior')
        self.assertEqual(self.char1.db.archetype, 'Warrior')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 6)
        self.assertEqual(+self.char1.traits.PER, 1)
        self.assertEqual(+self.char1.traits.INT, 1)
        self.assertEqual(+self.char1.traits.DEX, 4)
        self.assertEqual(+self.char1.traits.CHA, 4)
        self.assertEqual(+self.char1.traits.VIT, 6)
        self.assertEqual(+self.char1.traits.MAG, 0)

    def test_apply_scout(self):
        """confirm the Scout archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'scout')
        self.assertEqual(self.char1.db.archetype, 'Scout')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 4)
        self.assertEqual(+self.char1.traits.PER, 6)
        self.assertEqual(+self.char1.traits.INT, 6)
        self.assertEqual(+self.char1.traits.DEX, 4)
        self.assertEqual(+self.char1.traits.CHA, 1)
        self.assertEqual(+self.char1.traits.VIT, 1)
        self.assertEqual(+self.char1.traits.MAG, 0)

    def test_apply_arcanist(self):
        """confirm the Arcanist archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        self.assertEqual(self.char1.db.archetype, 'Arcanist')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 1)
        self.assertEqual(+self.char1.traits.PER, 4)
        self.assertEqual(+self.char1.traits.INT, 6)
        self.assertEqual(+self.char1.traits.DEX, 1)
        self.assertEqual(+self.char1.traits.CHA, 4)
        self.assertEqual(+self.char1.traits.VIT, 1)
        self.assertEqual(+self.char1.traits.MAG, 6)

    def test_apply_warrior_scout(self):
        """confirm the Warrior-Scout archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'warrior')
        archetypes.apply_archetype(self.char1, 'scout')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Scout')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 5)
        self.assertEqual(+self.char1.traits.PER, 3)
        self.assertEqual(+self.char1.traits.INT, 3)
        self.assertEqual(+self.char1.traits.DEX, 4)
        self.assertEqual(+self.char1.traits.CHA, 2)
        self.assertEqual(+self.char1.traits.VIT, 3)
        self.assertEqual(+self.char1.traits.MAG, 0)
        # reset and test opposite order
        archetypes.apply_archetype(self.char1, 'scout', reset=True)
        archetypes.apply_archetype(self.char1, 'warrior')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Scout')

    def test_apply_warrior_arcanist(self):
        """confirm the Warrior-Arcanist archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'warrior')
        archetypes.apply_archetype(self.char1, 'arcanist')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Arcanist')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 3)
        self.assertEqual(+self.char1.traits.PER, 2)
        self.assertEqual(+self.char1.traits.INT, 3)
        self.assertEqual(+self.char1.traits.DEX, 2)
        self.assertEqual(+self.char1.traits.CHA, 4)
        self.assertEqual(+self.char1.traits.VIT, 3)
        self.assertEqual(+self.char1.traits.MAG, 3)
        # reset and test opposite order
        archetypes.apply_archetype(self.char1, 'arcanist', reset=True)
        archetypes.apply_archetype(self.char1, 'warrior')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Arcanist')

    def test_apply_arcanist_scout(self):
        """confirm the Arcanist-Scout archetype is initialized correctly"""
        archetypes.apply_archetype(self.char1, 'arcanist')
        archetypes.apply_archetype(self.char1, 'scout')
        self.assertEqual(self.char1.db.archetype, 'Arcanist-Scout')
        self.assertEqual(set(archetypes.ALL_TRAITS),
                         set(self.char1.db.traits.keys()))
        self.assertEqual(+self.char1.traits.STR, 2)
        self.assertEqual(+self.char1.traits.PER, 5)
        self.assertEqual(+self.char1.traits.INT, 6)
        self.assertEqual(+self.char1.traits.DEX, 2)
        self.assertEqual(+self.char1.traits.CHA, 2)
        self.assertEqual(+self.char1.traits.VIT, 1)
        self.assertEqual(+self.char1.traits.MAG, 3)
        # reset and test opposite order
        archetypes.apply_archetype(self.char1, 'scout', reset=True)
        archetypes.apply_archetype(self.char1, 'arcanist')
        self.assertEqual(self.char1.db.archetype, 'Arcanist-Scout')

    def test_invalid_apply_sequence(self):
        """test invalid archetype assignment sequences"""
        # cannot assign the same archetype twice
        archetypes.apply_archetype(self.char1, 'scout')
        with self.assertRaises(archetypes.ArchetypeException):
            archetypes.apply_archetype(self.char1, 'scout')
        # cannot assign triple archetype
        archetypes.apply_archetype(self.char1, 'warrior')
        self.assertEqual(self.char1.db.archetype, 'Warrior-Scout')
        with self.assertRaises(archetypes.ArchetypeException):
            archetypes.apply_archetype(self.char1, 'arcanist')


class PublicFunctionsTestCase(EvenniaTest):
    """Test case for the supporting module functions."""
    character_typeclass = Character

    def setUp(self):
        super(PublicFunctionsTestCase, self).setUp()
        archetypes.apply_archetype(self.char1, 'warrior')

    def test_valid_allocations(self):
        """confirm valid trait allocations"""
        # warriors have 8 points to allocate
        self.char1.traits.STR.base += 2
        self.char1.traits.PER.base += 1
        self.char1.traits.INT.base += 1
        self.char1.traits.DEX.base += 1
        self.char1.traits.CHA.base += 1
        self.char1.traits.VIT.base += 2
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertEqual(sum(+self.char1.traits[t]
                             for t in archetypes.PRIMARY_TRAITS), 30)
        self.assertTrue(is_valid)
        # smartest warrior ever
        archetypes.apply_archetype(self.char1, 'warrior', reset=True)
        self.char1.traits.INT.base += 8
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertTrue(is_valid)

    def test_toomany_points(self):
        """confirm validation of over-allocated traits"""
        # perfect char not allowed
        for t in archetypes.PRIMARY_TRAITS:
            self.char1.traits[t].base = 10
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertFalse(is_valid)
        self.assertEqual(errmsg, 'Too many trait points allocated.')
        # no more than 30 allowed
        archetypes.apply_archetype(self.char1, 'warrior', reset=True)
        self.char1.traits.INT.base += 9
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertFalse(is_valid)
        self.assertEqual(errmsg, 'Too many trait points allocated.')

    def test_toofew_points(self):
        """confirm validation of under-allocated traits"""
        # fails before any allocations happen
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertFalse(is_valid)
        self.assertEqual(errmsg, 'Not enough trait points allocated.')
        # no less than 30 allowed
        self.char1.traits.INT.base += 6
        is_valid, errmsg = archetypes.validate_primary_traits(self.char1.traits)
        self.assertFalse(is_valid)
        self.assertEqual(errmsg, 'Not enough trait points allocated.')

    def test_calculate_secondary_traits(self):
        """confirm functionality of `calculate_secondary_traits` function"""
        self.char1.traits.STR.base += 3
        self.char1.traits.DEX.base += 2
        self.char1.traits.VIT.base += 3
        archetypes.calculate_secondary_traits(self.char1.traits)
        self.assertEqual(+self.char1.traits.HP, 9)
        self.assertEqual(+self.char1.traits.SP, 9)
        self.assertEqual(+self.char1.traits.FORT, 9)
        self.assertEqual(+self.char1.traits.REFL, 6)
        self.assertEqual(+self.char1.traits.WILL, 1)
        self.assertEqual(+self.char1.traits.ATKM, 9)
        self.assertEqual(+self.char1.traits.ATKR, 1)
        self.assertEqual(+self.char1.traits.ATKU, 6)
        self.assertEqual(+self.char1.traits.DEF, 6)
        self.assertEqual(self.char1.traits.ENC.max, 180)

    def test_load_archetype(self):
        """confirm `load_archetype` returns correct class instance"""
        at = archetypes.load_archetype('warrior')
        self.assertEqual(at.name, 'Warrior')
        self.assertEqual(at.health_roll, '1d6+1')
        at = archetypes.load_archetype('scout')
        self.assertEqual(at.name, 'Scout')
        self.assertEqual(at.health_roll, '1d6')
        at = archetypes.load_archetype('arcanist')
        self.assertEqual(at.name, 'Arcanist')
        self.assertEqual(at.health_roll, '1d6-1')
        at = archetypes.load_archetype('warrior-arcanist')
        self.assertEqual(at.name, 'Warrior-Arcanist')
        self.assertEqual(at.health_roll, '1d6-1')
        at = archetypes.load_archetype('warrior-scout')
        self.assertEqual(at.name, 'Warrior-Scout')
        self.assertEqual(at.health_roll, '1d6')
        at = archetypes.load_archetype('arcanist-scout')
        self.assertEqual(at.name, 'Arcanist-Scout')
        self.assertEqual(at.health_roll, '1d6-1')


