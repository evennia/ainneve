#
# Commands and cmdsetRelated to the equip handler
#
from evennia import CmdSet, utils
from evennia import Command

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
    wield = False

    def func(self):
        "implements the command."

        caller = self.caller
        args = self.args.strip()
        wield = self.wield

        # reset flag, this should stay at the beginning of the command
        if wield:
            self.wield = False

        if not args:
            caller.msg("Wear what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        if not obj in caller.contents:
            caller.msg("You don't have %s in your inventory." % obj)

        slots = utils.make_iter(obj.db.slot)

        if wield:
            if not caller.equip.primary_hand in slots     \
              and not caller.equip.secondary_hand in slots:
                caller.msg("You can't wield %s." % obj)
                return

        # equip primary and secondary hands with the proper feedback
        if caller.equip.primary_hand in slots  \
           or caller.equip.secondary_hand in slots:
            action = 'wield'
        else:
            action = 'wear'

        if not obj.db.slot or not obj.access(caller, 'equip'):
            caller.msg("You can't equip %s." % obj)
            return

        if obj in caller.equip.items:
            caller.msg("You're already %sing %s." % (action, obj.name))
            return

        if not caller.equip.add(obj):
            string = "You can't equip %s." % obj
            if [slot for slot in slots if slot in caller.equip.slots]:
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
    locks = "cmd:all()"

    def func(self):
        "implements the command."
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wield what?")
            return

        cmd = self.cmdset.get("wear")
        cmd.wield = True
        caller.execute_cmd("wear %s" % args)


class CmdHold(Command):
    """
    hold

    Usage:
      hold <obj>

    Hold an object.

    """
    key = "hold"
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

        if obj in caller.equip.items:
            caller.msg("You're already holding %s." % obj)
            return

        if not 'holds' in caller.equip.slot:
            caller.msg("You can't hold %s." % obj)
            return

        if caller.equip.get('holds'):
            caller.msg("You can't hold %s. You're already holding something.")
            return

        # call hook
        if hasattr(obj, "at_hold"):
            obj.at_hold(caller)

        # Hold command calls 'set' directly, not 'add'
        caller.equip.set('holds', obj)

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

        if not obj in caller.equip.items:
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

