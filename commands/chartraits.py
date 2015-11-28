"""
Character trait-related commands
"""

from .command import MuxCommand
from evennia.commands.cmdset import CmdSet
from evennia.utils.evform import EvForm
from evennia.utils.evtable import EvTable, EvColumn, EvCell


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
        tr = self.caller.traits
        sk = self.caller.skills

        fields = {
            'A': self.caller.name,
            'B': self.caller.db.archetype,
            'C': tr.XP.actual,
            'D': tr.XP.level_boundaries[tr.LV.actual],
            'E': tr.LV.actual,
            'F': tr.STR.actual,
            'G': tr.PER.actual,
            'H': tr.INT.actual,
            'I': tr.DEX.actual,
            'J': tr.CHA.actual,
            'K': tr.VIT.actual,
            'L': tr.MAG.actual,
            'M': tr.FORT.actual,
            'N': tr.REFL.actual,
            'O': tr.WILL.actual,
            'P': tr.ATKM.actual,
            'Q': tr.ATKR.actual,
            'R': tr.ATKU.actual,
            'S': tr.DEF.actual,
            'T': "{:+d}".format(tr.PP.actual),
            'U': tr.ENC.actual,
            'V': tr.ENC.max,
            'W': tr.MV.mod,
            'X': tr.MV.actual,
        }
        bold = lambda v: "{{w{}{{n".format(v)
        form.map({k: bold(v) for k, v in fields.iteritems()})

        desc = EvTable(header=False,
                       align='l',
                       table=[[self.caller.long_desc]],
                       border=None)

        gauges = EvTable(
            "{CHP{n", "{CSP{n", "{CBM{n", "{CWM{n",
            table=[["{} / {}".format(bold(tr.HP.actual), bold(tr.HP.max))],
                   ["{} / {}".format(bold(tr.SP.actual), bold(tr.SP.max))],
                   ["{} / {}".format(bold(tr.BM.actual), bold(tr.BM.max))],
                   ["{} / {}".format(bold(tr.WM.actual), bold(tr.WM.max))]],
            align='c',
            border="incols"
        )
        skill_names = sk.all
        third = len(skill_names) // 3
        skills = EvTable(
            header=False,
            align='l',
            table=[EvColumn(*["{{M{}{{n".format(sk[s].name)
                              for s in skill_names[:third]]),
                   EvColumn(*["{{w{}{{n".format(sk[s].actual)
                              for s in skill_names[:third]],
                            align='r'),
                   EvColumn(*["{{M{}{{n".format(sk[s].name)
                              for s in skill_names[third:2 * third]]),
                   EvColumn(*["{{w{}{{n".format(sk[s].actual)
                              for s in skill_names[third:2 * third]],
                            align='r'),
                   EvColumn(*["{{M{}{{n".format(sk[s].name)
                              for s in skill_names[2 * third:]]),
                   EvColumn(*["{{w{}{{n".format(sk[s].actual)
                              for s in skill_names[2 * third:]],
                            align='r'),
                   ]
        )

        form.map(tables={1: gauges, 2: desc, 3: skills})

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
    arg_regex = r"\s.+|"

    def func(self):
        from world import archetypes
        table = None
        tr = self.caller.traits
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
            traits = [["{{C{}{{n".format(tr.ENC.name),
                       "{CEncumbrance Penalty{n",
                       "{{C{}{{n".format(tr.MV.name)],
                      ["{{w{}{{n / {{w{}{{n".format(tr.ENC.actual,
                                                    tr.ENC.max),
                       "{{w{:+d}{{n".format(tr.MV.mod),
                       "{{w{}{{n".format(tr.MV.actual)]]

            table = EvTable(header=False, table=traits)
        else:
            self.caller.msg("Usage: traits <traitgroup>")
            return
        if not table:
            table = EvTable(
                header=False,
                table=[["{{C{}{{n".format(tr[t].name)
                        for t in traits],
                       ["{{w{}{{n".format(tr[t].actual)
                        for t in traits]]
            )

        self.caller.msg("{{R[ {{Y{}{{n {{R]{{n".format(title))
        self.caller.msg(unicode(table))
