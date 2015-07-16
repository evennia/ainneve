#
# Commands and CmdSetRelated for general player purposes
#
from evennia import CmdSet, utils
from evennia import Command


class GeneralCmdSet(CmdSet):

    key = "general_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdPrompt())

class CmdPrompt(Command):
    """
    prompt

    Usage:
        prompt <prompt string>

    Examples:
        prompt *hn*:hp *mn*:mana *mnn*:moves >
        prompt - displays your current prompt

    Available options that be included in the prompt string:
        *hn*    - current hp
        *hm*    - maximum hp
        *mn*    - current mana
        *mm*    - maximum mana
        *mnm*   - current moves
        *mmm*   - maximum moves

    Set the characters prompt

    """
    key = "prompt"
    locks = "cmd:all()"

    def parse(self):
        if self.args and len(self.args) <= 30:
            self.prompt = self.args.lstrip()
        else:
            self.prompt = None
            self.caller.msg('Prompt length is too long')

    def func(self):
        caller = self.caller
        new_prompt = self.prompt

        if not new_prompt:
            current_prompt = caller.db.prompt
            current_prompt = current_prompt.replace('\n','')
            caller.msg('{wCurrent prompt msg{n: %s' % current_prompt)
            caller.show_prompt('translate_only',caller.db.prompt)
        else:
            new_prompt = new_prompt.replace('\\n', '').lstrip()
            caller.msg('New prompt has been set: %s' % new_prompt)
            new_prompt = '\n' + new_prompt + ' '
            caller.db.prompt = new_prompt
