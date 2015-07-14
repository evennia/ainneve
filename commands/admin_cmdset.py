#
# Commands and cmdset applicable to admins
#
import os
from evennia import CmdSet, utils
from evennia import Command
from world.databases.skill_db import skill_db
from world.databases.spell_db import spell_db

class AdminCmdSet(CmdSet):

    key = "admin_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdSaveSkills())
        self.add(CmdSaveSpells())


# Add admin specific commands below

class CmdSaveSkills(Command):
    """
    saveskills

    Usage:
      saveskills

    Allows an admin to save skill_db stored in memory to file [skill_db.py]

    """
    key = "saveskills"
    alias = ["saveskill"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        SKILL_DB_DIR = os.getcwd()
        SKILL_DB_FILE = "skill_db.py"

        write_path = os.path.join(SKILL_DB_DIR, "world", "databases", SKILL_DB_FILE)

        # Save the memory contents of skill_db to skill_db.py
        caller.msg('Saving skill_db to: %s ...' % write_path)

        #-----------------------------------------------------------
        # Define imports and initalise the database
        #-----------------------------------------------------------
        output = 'from world.abilities.ability import Ability\n'
        output += '\n'
        output += '#Create the skills database\n'
        output += 'skill_db = {}\n'
        output += '\n'
        #------------------------------------------------------------
        # Iterate over every skill and create an Ability instance
        #------------------------------------------------------------
        output += '#Initalise every skill\n'
        for skill in skill_db:
            output += 'skill_db[\'%s\'] = Ability()\n' % skill
        #------------------------------------------------------------
        # Iterate over every skill and save the existing attributes
        #------------------------------------------------------------
        for skill in skill_db:
            output += '\n'
            output += '# %s skill\n' % skill
            keys = ([k for k in dir(skill_db[skill]) if not k.startswith('__')])
            for key in keys:
                value = getattr(skill_db[skill], key)
                if isinstance(value,str):
                    value = '\'' + value + '\''
                output +='skill_db[\'%s\'].%s = %s\n' % (skill,key,value)
        output +='\n'
        #------------------------------------------------------------
        # Write the actual output to a file
        #------------------------------------------------------------
        with open(write_path, 'w') as f:
            f.write(output)
        caller.msg('Skills have been saved.')


class CmdSaveSpells(Command):
    """
    savespells

    Usage:
      savespells

    Allows an admin to save spell_db stored in memory to file [spell_db.py]

    """
    key = "savespells"
    alias = ["savespell"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        SPELL_DB_DIR = os.getcwd()
        SPELL_DB_FILE = "spell_db.py"

        write_path = os.path.join(SPELL_DB_DIR, "world", "databases", SPELL_DB_FILE)

        # Save the memory contents of spell_db to spells_db.py
        caller.msg('Saving spells_db to: %s ...' % write_path)

        #-----------------------------------------------------------
        # Define imports and initalise the database
        #-----------------------------------------------------------
        output = 'from world.abilities.ability import Ability\n'
        output += '\n'
        output += '#Create the spells database\n'
        output += 'spell_db = {}\n'
        output += '\n'
        #------------------------------------------------------------
        # Iterate over every spell and create an Ability instance
        #------------------------------------------------------------
        output += '#Initalise every spell\n'
        for spell in spell_db:
            output += 'spell_db[\'%s\'] = Ability()\n' % spell
        #------------------------------------------------------------
        # Iterate over every spell and save the existing attributes
        #------------------------------------------------------------
        for spell in spell_db:
            output += '\n'
            output += '# %s spell\n' % spell
            keys = ([k for k in dir(spell_db[spell]) if not k.startswith('__')])
            for key in keys:
                value = getattr(spell_db[spell], key)
                if isinstance(value,str):
                    value = '\'' + value + '\''
                output +='spell_db[\'%s\'].%s = %s\n' % (spell,key,value)
        output +='\n'
        #------------------------------------------------------------
        # Write the actual output to a file
        #------------------------------------------------------------
        with open(write_path, 'w') as f:
            f.write(output)
        caller.msg('spells have been saved.')