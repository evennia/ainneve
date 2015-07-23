from evennia import CmdSet, utils
from evennia import Command
from world.config.spellmanager import spell_manager
from world.config.skillmanager import skill_manager
from evennia.utils.prettytable import PrettyTable

class GeneralCmdSet(CmdSet):

    key = "general_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdAbilities())

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

        caller.msg('********************************************************')
        caller.msg('{y           %s current abilities {n                    ' % caller)
        caller.msg('********************************************************')
        self.show_ability_skills()
        self.show_ability_spells()


    def show_ability_skills(self):
        caller = self.caller

        HEADER_OUTPUT = ['Skill','Level','Description',]
        table = PrettyTable()
        table._set_field_names(HEADER_OUTPUT)
        if caller.db.skills:
            caller.msg('\n{wYou have learnt the following skills:{n')
            for skill in caller.db.skills:
                table.add_row([
                    '{G%s' % skill_manager[skill].name,
                    '{R%s' % skill_manager[skill].level,
                    '{Y%s' % skill_manager[skill].description,
                ])

        table_text = table.get_string()
        caller.msg(table_text)

    def show_ability_spells(self):
        caller = self.caller

        HEADER_OUTPUT = ['Spell','Level','Description',]
        table = PrettyTable()
        table._set_field_names(HEADER_OUTPUT)
        if caller.db.skills:
            caller.msg('\n{wYou have learnt the following spells:{n')
            for spell in caller.db.spells:
                table.add_row([
                    '{G%s' % spell_manager[spell].name,
                    '{R%s' % spell_manager[spell].level,
                    '{Y%s' % spell_manager[spell].description,
                ])

        table_text = table.get_string()
        caller.msg(table_text)
