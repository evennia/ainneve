"""
Item commands.
"""

from evennia import CmdSet
from evennia.utils import delay
from command import Command

ACTIVATE_COST = (0, 'activate')


class EmpoweredArmorCmdSet(CmdSet):

    priority = 5
    cmdset_key = 'emp_armor'

    def at_cmdset_creation(self):
        self.add(ParryCommand())


class ParryCommand(Command):
    """
    boost defense temporarily

    Usage:
        parry

    Take a defensive stance that will temporarily
    reduce damage taken.
    """
    key = 'parry'
    aliases = ['par']
    locks = 'cmd:holds()'
    help_category = 'Combat'
    def func(self):
        char, obj = self.caller, self.obj
        cost = obj.db.ability_cost
        buff = 1
        if ACTIVATE_COST in cost:
            if obj.db.activated:
                char.msg('You are already parrying in {}.'.format(obj.key))
                return
            else:
                obj.db.activated = True
                cost.remove(ACTIVATE_COST)

        for amt, what in cost:
            if what == 'PP':
                if amt == 'all':
                    if char.traits.PP.actual > 0:
                        buff = char.traits.PP.actual
                        cost.remove(('all', 'PP'))
                    else:
                        char.msg('You have no Power Points to spend.')
                        return
                msg = 'Feeling a rush of power, your focus boosts your defenses'
            elif what == 'SP':
                msg = 'You prepare to stand steadfast against the onslaught'
        if all(char.traits[c[1]].actual >= c[0] for c in cost):

                char.traits[what].current -= amt
            char.traits.DEF.mod += 1

            delay(10, char, self.obj, callback=self.unparry)

    def unparry(self, char, obj, buff):
        """callback to reset parry effect"""

