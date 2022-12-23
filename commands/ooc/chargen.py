from evennia.commands.default.account import CmdCharCreate as DefaultCmdCharCreate

from world.chargen import start_chargen


class CmdCharCreate(DefaultCmdCharCreate):

    def func(self):
        account = self.account
        start_chargen(account, session=self.session)
