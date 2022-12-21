from evadventure.chargen import start_chargen
from evennia.commands.default.account import CmdCharCreate as DefaultCmdCharCreate


class CmdCharCreate(DefaultCmdCharCreate):

    def func(self):
        account = self.account
        start_chargen(account, session=self.session)
