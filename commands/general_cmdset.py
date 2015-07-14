from evennia import CmdSet, utils
from evennia import Command
from world.abilities.ability import Ability
from world.abilities.spell_db import spell_db
from world.abilities.skill_db import skill_db
from evennia.utils import evtable


class GeneralCmdSet(CmdSet):

    key = "general_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdAbilities())
        self.add(CmdLearn())
        self.add(CmdUnlearn())

class CmdAbilities(Command):
    """
    abilities

    Usage:
      abilities

    Show the player abilities

    """
    key = "abilities"
    aliases = ["abil","abi","spell","skill"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller


        skill_table = evtable.EvTable("{wSkill{n",
                                      "{wLevel{n",
                                      "{wDescription{n",
                                       table=[],
                                       border="cells")

        spell_table = evtable.EvTable("{wSpell{n",
                                      "{wLevel{n",
                                      "{wDescription{n",
                                       table=[],
                                       border="cells")

        caller.msg('**************************************************')
        caller.msg('{y           %s current abilities {n              ' % caller)
        caller.msg('**************************************************\n')

        if caller.db.skills:
            caller.msg('\n{wYou have learnt the following skills:{n')
            for skill in caller.db.skills:
                skill_table.add_row('%s' % caller.db.skills[skill].name,
                                    '%s' % caller.db.skills[skill].level,
                                    '%s' % caller.db.skills[skill].description)
            skill_table.reformat_column(0,width=15)
            caller.msg(skill_table)

        if caller.db.spells:
            caller.msg('\n{wYou have learnt the following spells:{n')
            for spell in caller.db.spells:
                spell_table.add_row('%s' % caller.db.spells[spell].name,
                                    '%s' % caller.db.spells[spell].level,
                                    '%s' % caller.db.spells[spell].description)
            spell_table.reformat_column(0,width=15)
            caller.msg(spell_table)


class CmdLearn(Command):
    """
    general learn command

    Usage:
      learn <skill/spell> <value>

    Lets the player learn new skills or spells

    """
    key = "learn"
    locks = "cmd:all()"

    def parse(self):
        self.args = self.args.split()
        self.valid_syntax = False
        self.type = None
        self.value = None

        if len(self.args) == 2 and self.args[0] in ('skill','spell'):
            self.type = self.args[0]
            self.value = self.args[1]
            self.valid_syntax = True

    def func(self):
        caller = self.caller
        type = self.type
        spell = self.value
        skill = self.value

        if not self.args:
            self.list_skills()
            self.list_spells()
            caller.msg('\n{wsyntax:{n [learn] <skill/spell> <value>')
            return

        if not self.valid_syntax:
            caller.msg('\n{wsyntax:{n [learn] <skill/spell> <value>')
            return

        if 'skill' in type and self.can_learn_skill(skill):
            new_skill = self.get_skill(skill)
            caller.db.skills[skill] = new_skill
            caller.msg('You have learnt the \'%s\' skill' % skill)

        elif 'spell' in type and self.can_learn_spell(spell):
            new_spell = self.get_spell(spell)
            caller.db.spells[spell] = new_spell
            caller.msg('You have learnt the \'%s\' spell' % spell)

        elif caller.has_skill(skill) or caller.has_spell(spell):
            caller.msg('You have already mastered this ability.')
        else:
            caller.msg('You may not learn that!')


    # Check to see if the caller can learn the skill
    # - Does the caller already have the skill?
    # - Has the skill been defined in skill_db.py?
    def can_learn_skill(self,skill):
        if self.caller.has_skill(skill):
            return False
        if not self.get_skill(skill):
            return False
        return True

    # Check to see if the caller can learn the spell
    # - Does the caller already have the spell?
    # - Has the spell been defined in spell_db.py?
    def can_learn_spell(self,spell):
        if self.caller.has_spell(spell):
            return False
        if not self.get_spell(spell):
            return False
        return True

    # List all skills that have been defined in skill_db.py
    def list_skills(self):
        caller = self.caller
        caller.msg('**************************************************')
        caller.msg('{y     The following skills are available   {n    ')
        caller.msg('**************************************************\n')
        skill_table = evtable.EvTable("{wSkill{n",
                                      "{wDescription{n",
                                       table=[],
                                       border="cells")
        if skill_db:
            for skill in skill_db:
                skill_table.add_row('%s' % skill_db[skill].name,
                                    '%s' % skill_db[skill].description)
        else:
            skill_table.add_row('None', 'N/A')
        caller.msg(skill_table)

    # List all spells that have been defined in spell_db.py
    def list_spells(self):
        caller = self.caller
        caller.msg('\n**************************************************')
        caller.msg('{y     The following spells are available   {n    ')
        caller.msg('**************************************************\n')
        spell_table = evtable.EvTable("{wSpell{n",
                                      "{wDescription{n",
                                       table=[],
                                       border="cells")
        if spell_db:
            for spell in spell_db:
                spell_table.add_row('%s' % spell_db[spell].name,
                                    '%s' % spell_db[spell].description)
        else:
            spell_table.add_row('None', 'N/A')
        caller.msg(spell_table)

    # Determine whether the skill has been defined [skill_db.py]
    def get_skill(self,skill):
        try:
            return skill_db[skill]
        except KeyError:
            return False

    # Determine whether the spell has been defined [spell_db.py]
    def get_spell(self,spell):
        try:
            return spell_db[spell]
        except KeyError:
            return False



class CmdUnlearn(Command):
    """
    general unlearn command

    Usage:
      unlearn <skill/spell> <value>

    Lets the player unlearn skills or spells

    """
    key = "unlearn"
    locks = "cmd:all()"

    def parse(self):

        self.args = self.args.split()
        self.valid_syntax = False
        self.type = None
        self.value = None

        if len(self.args) == 2 and self.args[0] in ('skill','spell'):
            self.type = self.args[0]
            self.value = self.args[1]
            self.valid_syntax = True

    def func(self):
        caller = self.caller
        type = self.type
        spell = self.value
        skill = self.value

        if not self.valid_syntax:
            caller.msg('{wsyntax:{n unlearn <skill/spell> <value>')
            return

        # Unlearn the skill if the character has it
        if 'skill' in type and caller.has_skill(skill):
            del caller.db.skills[skill]
            caller.msg('You unlearn \'%s\' skill' % skill)
            return
        elif 'skill' in type:
            caller.msg('You do not know this skill!')

        # Unlearn the spell if the character has it
        if 'spell' in type and caller.has_spell(spell):
            del caller.db.spells[spell]
            caller.msg('You unlearn \'%s\' spell' % spell)
            return
        elif 'spell'in type:
            caller.msg('You do not know this spell!')
