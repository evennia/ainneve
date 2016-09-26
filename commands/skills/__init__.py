from evennia.commands.cmdset import CmdSet
from commands.skills.appraise import CmdAppraise

class SkillCmdSet(CmdSet):
    key = "Skill"
    def at_cmdset_creation(self):
        self.add(CmdAppraise)
