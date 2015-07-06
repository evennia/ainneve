#    @property
#    def short_desc(self):
#        return self.db.short_desc
#    
#    @short_desc.setter
#    def short_desc(self, value):
#        if not value:
#            pass
#        else:
#            self.db.short_desc = str(value)

from commands.command import MuxCommand
from evennia import CmdSet, utils

class BuildCmdSet(CmdSet):

    key = "build_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdFlag())

class CmdFlag(MuxCommand):
    """
    This is the command used to apply room's FLAGS.
    Flags are picked from the following list:
    
    * is_indoor
    * is_dark
    * is_safe
    * has_road
    * no_magic
    * no_teleport
    * no_summon
    * is_silent
    * no_range
    * is_water
    * is_air
    * no_quit
        
    Usage:
    @flag[/switches] <obj> = <flag>
    
    Switches:
    /del = remove flag
    """
    
    key = "@flag"
    locks = "cmd:perm(flag) or cmd:perm(Builders)"
    help_category = "Building"
    
    def func(self):
        "Implement the Flag command"
        flags = (
            "is_indoor",
            "is_dark",
            "is_safe",
            "has_road",
            "no_magic",
            "no_teleport",
            "no_summon",
            "is_silent",
            "no_range",
            "is_water",
            "is_air",
            "no_quit"
            )
        if not self.args:
            self.caller.msg("Usage: @flag[/switches] <obj> = <flag>")
            return
        if "del" in self.switches:
            # remove one or all tags
            obj = self.caller.search(self.lhs, global_search=True)
            if not obj:
                return
            if self.rhs:
                # remove individual tag
                flag = self.rhs
                category = "flags"
                obj.tags.remove(flag, category=category)
                string = "Removed flag '%s'%s from %s (if it existed)" % (flag,
                                                    " (category: %s)" % category if category else "",
                                                    obj)
            else:
                # no tag specified, clear all tags
                obj.tags.clear()
                string = "Cleared all tags and flags from from %s." % obj
            self.caller.msg(string)
            return
        if self.rhs:
            # = is found, so we are on the form obj = tag
            obj = self.caller.search(self.lhs, global_search=True)
            if not obj:
                return
            flag = self.rhs
            category = "flags"
            if flag in flags:
                # create the tag
                obj.tags.add(flag, category=category)
                string = "Added flag '%s'%s to %s." % (flag,
                                                    " (category: %s)" % category if category else "",
                                                    obj)
                self.caller.msg(string)
            else:
                string = "'%s' is not a possible flag. You may add it as a tag (see help @tag)" % flag
                self.caller.msg(string)
        else:
            # no = found - list tags on object
            obj = self.caller.search(self.args, global_search=True)
            if not obj:
                return
            tagtuples = obj.tags.all(return_key_and_category=True)
            ntags = len(tagtuples)
            tags = [tup[0] for tup in tagtuples]
            categories = [" (category: %s)" % tup[1] if tup[1] else "" for tup in tagtuples]
            if ntags:
                string = "Tag%s on %s: %s" % ("s" if ntags > 1 else "", obj,
                                        ", ".join("'%s'%s" % (tags[i], categories[i]) for i in range(ntags)))
            else:
                string = "No tags attached to %s." % obj
            self.caller.msg(string)
