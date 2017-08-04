"""
Unit tests for Ainneve custom typeclasses.
"""
from evennia.utils.test_resources import EvenniaTest
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.characters import Character
from utils.utils import sample_char
from mock import Mock

class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

class DescriptionTestCase(EvenniaTest):
    """Test case for at_return_appearance hook"""
    character_typeclass = Character
    exit_typeclass = Exit
    room_typeclass = Room

    def setUp(self):
        super(DescriptionTestCase, self).setUp()
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        sample_char(self.char2, 'arcanist', 'elf', 'alertness')
        self.char1.msg = Mock()
        self.char2.msg = Mock()

    def test_look_at_self(self):
        self.char1.execute_cmd('look self')
        self.char1.msg.assert_called_once_with(AnyStringWith('the Human Warrior'))

    def test_race_and_arch_with_low_perception(self):
        self.char1.traits.PER.base = 0
        appearance = self.char2.return_appearance(self.char1)
        self.assertFalse('the Elf Arcanist' in appearance, 'Saw race and archetype with too low perception')

    def test_race_and_arch_with_high_perception(self):
        self.char1.traits.PER.base = 1000
        appearance = self.char2.return_appearance(self.char1)
        self.assertTrue('the Elf Arcanist' in appearance, 'Did not see race and archetype with very high perception')

    def test_health_and_stamina_with_low_perception(self):
        self.char1.traits.PER.base = 0
        self.char2.traits.HP.base = 10
        self.char2.traits.HP.current = 3

        appearance = self.char2.return_appearance(self.char1)
        self.assertTrue('They seem to be in good health.' in appearance, 'Saw correct health with low perception')
        self.assertFalse('They seem full of energy.' in appearance, 'Saw correct stamina with low perception')

class MovementTestCase(EvenniaTest):
    """Test case for movement rules."""
    character_typeclass = Character
    exit_typeclass = Exit
    room_typeclass = Room

    def setUp(self):
        super(MovementTestCase, self).setUp()
        sample_char(self.char1, 'warrior', 'human', 'cunning')
        self.char1.msg = Mock()

    def test_movement_nodelay(self):
        """test non-delayed movement"""
        self.assertEqual(self.char1.traits.MV.current, 5)
        self.char1.execute_cmd('out')
        self.assertEqual(self.char1.traits.MV.current, 4)
        self.assertEqual(self.char1.location, self.room2)

    def test_movement_delay(self):
        """test delayed movement"""
        self.room2.terrain = 'MODERATE'
        self.char1.execute_cmd('out')
        self.assertIn('You start moving out.',
                      (args[0] for name, args, kwargs
                       in self.char1.msg.mock_calls))
        self.assertNotEqual(self.char1.location, self.room2)
        self.assertEqual(self.char1.traits.MV.current, 5)

    def test_movement_exhaustion(self):
        """test messaging without enough MV points"""
        self.char1.traits.MV.current = 0
        self.char1.execute_cmd('out')
        self.assertIn('Moving so far so fast has worn you out. '
                      'You pause for a moment to gather your '
                      'composure.',
                      (args[0] for name, args, kwargs
                       in self.char1.msg.mock_calls))

    def test_double_movement(self):
        """test messaging without enough MV points"""
        self.room2.terrain = 'MODERATE'
        self.char1.execute_cmd('out')
        self.char1.execute_cmd('out')
        self.assertIn("You are aleady moving. Use the 'stop' "
                      "command and try again to change "
                      "destinations.",
                      (args[0] for name, args, kwargs
                       in self.char1.msg.mock_calls))

    def test_stop_movement(self):
        """test messaging without enough MV points"""
        self.room2.terrain = 'MODERATE'
        self.char1.execute_cmd('out')
        self.char1.execute_cmd('stop')
        self.assertIn("You stop moving.",
                      (args[0] for name, args, kwargs
                       in self.char1.msg.mock_calls))

    def test_stop_nomove(self):
        """test messaging without enough MV points"""
        self.room2.terrain = 'MODERATE'
        self.char1.execute_cmd('stop')
        self.assertIn("You are not moving.",
                      (args[0] for name, args, kwargs
                       in self.char1.msg.mock_calls))
