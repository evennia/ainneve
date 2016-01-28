"""
Unit tests for Ainneve custom typeclasses.
"""
from evennia.utils.test_resources import EvenniaTest
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.characters import Character
from utils.utils import sample_char
from mock import Mock


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
