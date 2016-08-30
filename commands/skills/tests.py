from commands.skills.appraise import CmdAppraise
from evennia.utils.test_resources import EvenniaTest
from evennia.commands.default.tests import CommandTest
from typeclasses.characters import Character
from utils.utils import sample_char

class AppraiseTestCase(CommandTest):
    character_typeclass = Character

    def setUp(self):
        super(AppraiseTestCase, self).setUp()
        sample_char(self.char1, 'arcanist', 'elf', 'spirit')

        self.obj1.db.weight = 1
        self.obj1.db.damage = 2
        self.obj1.db.toughness = 3
        self.obj1.db.range = 4
        self.obj1.db.value = 150

        self.obj2.db.weight = 1
        self.obj2.db.damage = 2
        self.obj2.db.toughness = 3
        self.obj2.db.range = 4
        self.obj2.db.value = 150

    def test_appraise_success(self):
        self.char1.skills.appraise.base = 10
        self.char1.execute_cmd('get Obj')

        # Succeed at appraising the item
        self.call(CmdAppraise(), 'Obj', "Value: 1 SC 50 CC\n" +
                                        "Weight: 1\n" +
                                        "Damage:  2 \n" +
                                        "Range:  4 \n" +
                                        "Toughness:  3")
        self.call(CmdAppraise(), 'Obj', "Value: 1 SC 50 CC\n" +
                                        "Weight: 1\n" +
                                        "Damage:  2 \n" +
                                        "Range:  4 \n" +
                                        "Toughness:  3")

    def test_appraise_failure(self):
        self.char1.skills.appraise.base = -10
        self.char1.execute_cmd('get Obj2')

        # Fail at appraising the item
        self.call(CmdAppraise(), 'Obj2', 
            "You cannot tell the qualities of Obj2.")

        # Prevent another attempt before the timer expires
        self.call(CmdAppraise(), 'Obj2', 
            "You have already attempted to appraise Obj2" + 
            " recently and must wait a while before trying again.")





