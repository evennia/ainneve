"""
Implements a base Command class for the game's commands.

"""

from evennia.commands.command import Command as BaseCommand


class Command(BaseCommand):
    """
    Base command. This is on the form

        command <args>

    where whitespace around the argument(s) are stripped.

    """

    def __init__(self, **kwargs):
        self.caller = None  # This line is to avoid the IDE complaints
        super().__init__(**kwargs)

    def parse(self):
        self.args = self.args.strip()
