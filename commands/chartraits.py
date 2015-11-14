"""
Character trait-related commands
"""

from .command import MuxCommand
from evennia.commands.cmdset import CmdSet
from evennia.utils.evform import EvForm, EvTable


class CharTraitCmdSet(CmdSet):

    key = "chartrait_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdSheet())
        self.add(CmdTraits())

class CmdSheet(MuxCommand):
    """
    view character status

    Usage:
      sheet

    Displays a summary of the your character's information.
    """
    key = "sheet"
    aliases = ["sh"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """
        Handle displaying status.
        """
        form = EvForm('commands.templates.charsheet', align='r')
        fields = {
            'A': self.caller.name,
            'B': self.caller.db.archetype,
            'C': +self.caller.traits.XP,
            'D': self.caller.traits.XP.level_boundaries[+self.caller.traits.LV],
            'E': +self.caller.traits.LV,
            'F': +self.caller.traits.STR,
            'G': +self.caller.traits.PER,
            'H': +self.caller.traits.INT,
            'I': +self.caller.traits.DEX,
            'J': +self.caller.traits.CHA,
            'K': +self.caller.traits.VIT,
            'L': +self.caller.traits.MAG,
            'M': +self.caller.traits.FORT,
            'N': +self.caller.traits.REFL,
            'O': +self.caller.traits.WILL,
            'P': +self.caller.traits.ATKM,
            'Q': +self.caller.traits.ATKR,
            'R': +self.caller.traits.ATKU,
            'S': +self.caller.traits.DEF,
            'T': "{:+d}".format(+self.caller.traits.PP),
            'U': +self.caller.traits.ENC,
            'V': self.caller.traits.ENC.max,
            'W': self.caller.traits.MV.mod,
            'X': +self.caller.traits.MV,
        }
        bold = lambda v: "{{w{}{{n".format(v)
        form.map({k: bold(v) for k, v in fields.iteritems()})

        desc = EvTable(header=False,
                       align='l',
                       table=[[self.caller.long_desc]],
                       border=None)

        gauges = EvTable("{CHP{n", "{CSP{n", "{CBM{n", "{CWM{n",
                         table=[[bold(+self.caller.traits.HP)],
                                [bold(+self.caller.traits.SP)],
                                [bold(+self.caller.traits.BM)],
                                [bold(+self.caller.traits.WM)]],
                         align='c',
                         border="incols")

        form.map(tables={1: gauges, 2: desc})

        self.caller.msg(unicode(form))



class CmdTraits(MuxCommand):
    """
    view character status

    Usage:
      traits <traitgroup>

    Args:
        traitgroup - one of pri[mary], sec[ondary], sav[es],
                     com[bat], enc[umbrance], or car[ry]

    Displays a summary of the your character's information.
    """
    key = "traits"
    aliases = ["trait", "tr"]
    locks = "cmd:all()"
    arg_regex = r"\s(?:pri|sec|sav|com|enc|car)|"

    def func(self):
        from world import archetypes
        table = None
        if self.args.startswith('pri'):
            title = 'Primary Traits'
            traits = archetypes.PRIMARY_TRAITS
        elif self.args.startswith('sec'):
            title = 'Secondary Traits'
            traits = archetypes.SECONDARY_TRAITS
        elif self.args.startswith('sav'):
            title = 'Save Rolls'
            traits = archetypes.SAVE_ROLLS
        elif self.args.startswith('com'):
            title = 'Combat Stats'
            traits = archetypes.COMBAT_TRAITS
        elif self.args.startswith('enc') or self.args.startswith('car'):
            title = 'Encumbrance'
            traits = [["{{C{}{{n".format(self.caller.traits.ENC.name),
                       "{CEncumbrance Penalty{n",
                       "{{C{}{{n".format(self.caller.traits.MV.name)],
                      ["{{w{}{{n / {{w{}{{n".format(+self.caller.traits.ENC,
                                                    self.caller.traits.ENC.max),
                       "{{w{:+d}{{n".format(self.caller.traits.MV.mod),
                       "{{w{}{{n".format(+self.caller.traits.MV)]]

            table = EvTable(header=False, table=traits)
        else:
            self.caller.msg("Usage: traits <traitgroup>")
            return
        if not table:
            table = EvTable(header=False,
                            table=[["{{C{}{{n".format(self.caller.traits[t].name)
                                    for t in traits],
                                   ["{{w{}{{n".format(+self.caller.traits[t])
                                    for t in traits]])

        self.caller.msg("{{R[ {{Y{}{{n {{R]{{n".format(title))
        self.caller.msg(unicode(table))
