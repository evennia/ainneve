"""
Character trait-related commands
"""

from .command import MuxCommand
from evennia.commands.cmdset import CmdSet
from evennia.utils.evform import EvForm, EvTable
from utils.ainnevelist import AinneveList


class CharTraitCmdSet(CmdSet):

    key = "chartrait_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdSheet())
        self.add(CmdTraits())
        self.add(CmdSkills())

class CmdSheet(MuxCommand):
    """
    view character status

    Usage:
      sheet[/skills]

    Switch:
      sk[ills] - also display a summary of all character skills

    Displays a detailed summary of your character's information.
    """
    key = "sheet"
    aliases = ["sh"]
    locks = "cmd:all()"

    def func(self):
        """
        Handle displaying status.
        """
        form = EvForm('commands.templates.charsheet', align='r')
        tr = self.caller.traits
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
            'Y': self.caller.db.race,
            'Z': self.caller.db.focus,
        }
        bold = lambda v: "{{w{}{{n".format(v)
        form.map({k: bold(v) for k, v in fields.iteritems()})

        gauges = EvTable(
            "|CHP|n", "|CSP|n", "|CBM|n", "|CWM|n",
            table=[["{} / {}".format(bold(tr.HP.actual), bold(tr.HP.max))],
                   ["{} / {}".format(bold(tr.SP.actual), bold(tr.SP.max))],
                   ["{} / {}".format(bold(tr.BM.actual), bold(tr.BM.max))],
                   ["{} / {}".format(bold(tr.WM.actual), bold(tr.WM.max))]],
            align='c',
            border="incols"
        )
        desc = EvTable(header=False,
                       align='l',
                       table=[[self.caller.long_desc]],
                       border=None)

        form.map(tables={1: gauges, 2: desc})

        self.caller.msg(unicode(form))

        if any(sw.startswith('sk') for sw in self.switches):
            self.caller.execute_cmd('skills')


class CmdTraits(MuxCommand):
    """
    view character status

    Usage:
      traits <traitgroup>

    Args:
        traitgroup - one of pri[mary], sec[ondary], sav[es],
                     com[bat], enc[umbrance], or car[ry]

    Displays a summary of your character's traits by group.
    """
    key = "traits"
    aliases = ["trait", "tr"]
    locks = "cmd:all()"
    arg_regex = r"\s.+|"

    def func(self):
        from world import archetypes
        table = None
        cols = 1
        fill_dir = 'h'
        tr = self.caller.traits
        if self.args.startswith('pri'):
            title = 'Primary Traits'
            traits = archetypes.PRIMARY_TRAITS
            cols = 3
        elif self.args.startswith('sec'):
            title = 'Secondary Traits'
            traits = archetypes.SECONDARY_TRAITS
            cols = 2
            fill_dir = 'v'
        elif self.args.startswith('sav'):
            title = 'Save Rolls'
            traits = archetypes.SAVE_ROLLS
            cols = 3
        elif self.args.startswith('com'):
            title = 'Combat Stats'
            traits = archetypes.COMBAT_TRAITS
            cols = 3
        elif self.args.startswith('enc') or self.args.startswith('car'):
            title = 'Encumbrance'
            traits = [{'lbl': tr.ENC.name,
                       'val': "{}|n / |w{}".format(tr.ENC.actual, tr.ENC.max),
                       'sort': 0},
                      {'lbl': "Encumbrance Penalty",
                       'val': "{:+d}".format(tr.MV.mod),
                       'sort': 1},
                      {'lbl': tr.MV.name,
                       'val': "{}".format(tr.MV.actual),
                       'sort': 2}]

            table = AinneveList(traits,
                                lcolor='|C',
                                vcolor='|w',
                                vwidth=9,
                                layout=['column-3'],
                                orderby='sort')
        else:
            self.caller.msg("Usage: traits <traitgroup>")
            return
        if not table:
            table = AinneveList({tr[t].name: tr[t].actual for t in traits},
                                columns=cols,
                                lcolor='|C',
                                vcolor='|w',
                                fill_dir=fill_dir,
                                orderby=lambda x: [tr[t].name for t
                                                   in traits].index(x['lbl']))

        self.caller.msg("  |Y{}|n".format(title))
        self.caller.msg(unicode(table))


class CmdSkills(MuxCommand):
    """
    view character skills

    Usage:
      skills <skillgroup>

    Args:
        skillgroup - one of str[ength], per[ception], int[elligence],
                     dex[terity], or cha[risma]

    Displays a summary of your character's skills by group.
    """
    key = "skills"
    aliases = ["skill", "sk"]
    locks = "cmd:all()"
    arg_regex = r"\s.+|"

    def func(self):
        from world import skills

        sk = self.caller.skills
        sk_list = []

        if len(self.args.strip()) > 0:
            if self.args.lower().startswith('str'):
                title = 'Strength Based Skills'
                sk_list = skills.STR_SKILLS
            elif self.args.lower().startswith('per'):
                title = 'Perception Based Skills'
                sk_list = skills.PER_SKILLS
            elif self.args.lower().startswith('int'):
                title = 'Intelligence Based Skills'
                sk_list = skills.INT_SKILLS
            elif self.args.lower().startswith('dex'):
                title = 'Dexterity Based Skills'
                sk_list = skills.DEX_SKILLS
            elif self.args.lower().startswith('cha'):
                title = 'Charisma Based Skills'
                sk_list = skills.CHA_SKILLS
            else:
                self.msg('Usage: skills [<skillgroup>]')
                return

            list = AinneveList(columns=3, lcolor='|M', vcolor='|w')
            list.data = {sk[s].name: sk[s].actual for s in sk_list}
        else:
            title = 'Skills'
            list = AinneveList(columns=3,
                               width=77,
                               lcolor='|M',
                               vcolor='|w',
                               orderby='sort')
            list.data = [
                {'lbl': sk.escape.name, 'val': sk.escape.actual, 'sort': 0},
                {'lbl': sk.climb.name, 'val': sk.climb.actual, 'sort': 1},
                {'lbl': sk.jump.name, 'val': sk.jump.actual, 'sort': 2},
                {'lbl': sk.lockpick.name, 'val': sk.lockpick.actual, 'sort': 3},
                {'lbl': sk.listen.name, 'val': sk.listen.actual, 'sort': 4},
                {'lbl': sk.sense.name, 'val': sk.sense.actual, 'sort': 5},
                {'lbl': sk.appraise.name, 'val': sk.appraise.actual, 'sort': 6},
                {'lbl': sk.medicine.name, 'val': sk.medicine.actual, 'sort': 7},
                {'lbl': sk.survival.name, 'val': sk.survival.actual, 'sort': 8},
                {'lbl': sk.balance.name, 'val': sk.balance.actual, 'sort': 9},
                {'lbl': sk.sneak.name, 'val': sk.sneak.actual, 'sort': 10},
                {'lbl': sk.throwing.name, 'val': sk.throwing.actual, 'sort': 11},
                {'lbl': sk.animal.name, 'val': sk.animal.actual, 'sort': 12},
                {'lbl': sk.barter.name, 'val': sk.barter.actual, 'sort': 13},
                {'lbl': sk.leadership.name, 'val': sk.leadership.actual, 'sort': 14},
            ]

        self.caller.msg("  |Y{}|n".format(title))
        self.caller.msg(unicode(list))
