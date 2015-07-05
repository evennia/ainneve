#
# Commands and cmdsetRelated to the equip handler
#
from evennia import CmdSet, utils
from commands.command import Command

class EquipCmdSet(CmdSet):

    key = "equip_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        "Populate CmdSet"
        self.add(CmdEquip())
        self.add(CmdWear())
        self.add(CmdWield())
        self.add(CmdHold())
        self.add(CmdRemove())

class CmdEquip(Command):
    """
    equip

    Usage:
      equip

    Show your current equipment.

    """
    key = "equip"
    aliases = ["eq"]
    locks = "cmd:all()"

    def func(self):
        "check equipment"
        caller = self.caller
        table = utils.prettytable.PrettyTable(["slot", "item"])
        table.header = False
        table.border = False
        for slot, item in caller.equip:
            if not item or not item.access(caller, 'view'):
                continue
            table.add_row(["{C%s{n" % slot.capitalize(), item.name.capitalize()])
        if not str(table):
            string = "You have nothing in your equipment."
        else:
            string = "{wYour equipment:\n%s" % table
        self.caller.msg(string)

class CmdWear(Command):
    """
    wear

    Usage:
      wear <obj>

    Wear an object.

    """
    key = "wear"
    locks = "cmd:all()"

    def func(self):
        "implements the command."

        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wear what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        if not obj in caller.contents:
            caller.msg("You don't have %s in your inventory." % obj)

        # equip primary and secondary hands with the proper feedback
        if 'right hand' in utils.make_iter(obj.db.slot)     \
           or 'left hand' in utils.make_iter(obj.db.slot):
            action = 'wield'
        else:
            action = 'wear'

        if not obj.db.slot or not obj.access(caller, 'equip'):
            caller.msg("You can't equip %s." % obj)
            return

        if obj in caller.equip.items():
            caller.msg("You're already %sing %s." % (action, obj.name))
            return

        if not caller.equip.add(obj):
            string = "You can't equip %s." % obj
            if [s for s in utils.make_iter(obj.db.slot) if s in caller.equip.slots]:
                string += " You already have something there."
            caller.msg(string)
            return

        # call hook
        if hasattr(obj, "at_equip"):
            obj.at_equip(caller)
        caller.msg("You %s %s." % (action, obj))
        caller.location.msg_contents("%s %ss %s." % (caller.name.capitalize(), action, obj),
                                     exclude=caller)


class CmdWield(Command):
    """
    wield

    Usage:
      wield <obj>

    Wield an object.

    """
    key = "wield"
    aliases = ["equip primary", "ep"]
    locks = "cmd:all()"
    obj_to_wield = None

    def func(self):
        "implements the command."
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wield what?")
            return

        caller.execute_cmd("wear %s" % args)

class CmdHold(Command):
    """
    hold

    Usage:
      hold <obj>

    Hold an object.

    """
    key = "hold"
    aliases = ["equip secondary", "es"]
    locks = "cmd:all()"

    def func(self):
        "implements the command."
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Hold what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        if not obj in caller.contents:
            caller.msg("You don't have %s in your inventory." % obj)
            return

        if not obj.access(caller, 'hold'):
            caller.msg("You can't hold %s." % obj)
            return

        if obj in caller.equip.items():
            caller.msg("You're already holding %s." % obj)
            return

        if not caller.equip.add(obj):
            string = "You can't hold %s." % obj
            if caller.equip.get('holds'):
                string += " You already have something there."
            caller.msg(string)
                
            return

        # call hook
        if hasattr(obj, "at_hold"):
            obj.at_hold(caller)

        caller.msg("You hold %s." % obj)
        caller.location.msg_contents("%s holds %s." % (caller.name.capitalize(), obj),
                                     exclude=caller)


class CmdRemove(Command):
    """
    remove

    Usage:
      remove <obj>

    Remove an object from equip.

    """
    key = "remove"
    aliases = ["rem"]
    locks = "cmd:all()"

    def func(self):
        "implements the command."

        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Remove what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        if not obj in caller.equip.items():
            caller.msg("You are not wearing %s." % obj)
            return
        if not caller.equip.remove(obj):
            return

        # call hook
        if hasattr(obj, "at_remove"):
            obj.at_remove(caller)

        caller.msg("You remove %s." % obj)
        caller.location.msg_contents("%s removes %s." % (caller.name.capitalize(), obj),
                                         exclude=caller)

