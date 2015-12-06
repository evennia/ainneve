"""
Item and equipment-related command module.
"""
from evennia import CmdSet
from commands.command import Command, MuxCommand
from evennia.utils.evtable import EvTable
from typeclasses.items import Equippable


__all__ = ('CmdInventory', 'CmdEquip',
           'CmdWear', 'CmdWield', 'CmdRemove')


class EquipCmdSet(CmdSet):
    """CmdSet for item / equip commands."""
    key = "equip_cmdset"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdInventory())
        self.add(CmdEquip())
        self.add(CmdWear())
        self.add(CmdWield())
        self.add(CmdRemove())


class CmdInventory(MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        items = [i for i in self.caller.contents
                 if i not in self.caller.equip]
        if not items:
            string = "You are not carrying anything."
        else:
            data = [[],[]]
            for item in items:
                data[0].append("|C{}|n".format(item.name))
                data[1].append(item.db.desc or "")
            table = EvTable(header=False, table=data, border=None)
            string = "|YYou are carrying:|n\n{}".format(table)
        self.caller.msg(string)


class CmdEquip(MuxCommand):
    """
    view equipment

    Usage:
      equip

    Shows your current equipment.
    """
    key = "equip"
    aliases = ["eq"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        data = []
        s_width = max(len(s) for s in caller.equip.slots)
        for slot, item in caller.equip:
            if not item or not item.access(caller, 'view'):
                continue
            data.append(
                "  |b{slot:>{swidth}.{swidth}}|n: {item}".format(
                    slot=slot.capitalize(),
                    swidth=s_width,
                    item=item.name
                )
            )
        if len(data) <= 0:
            output = "You have nothing in your equipment."
        else:
            table = EvTable(header=False, border=None, table=[data])
            output = "|YYour equipment:|n\n{}".format(table)

        self.caller.msg(output)


class CmdWear(MuxCommand):
    """
    wear an item

    Usage:
      wear <obj>

    Equips an item from your inventory to an available non-weapon
    equipment slot on your character.
    """
    key = "wear"
    locks = "cmd:all()"
    wield = False

    def func(self):
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

        if obj not in caller.contents:
            caller.msg(
                "You don't have {} in your inventory.".format(obj.name))
            return

        if wield:
            if not any(s.startswith('wield') for s in obj.db.slots):
                caller.msg("You can't wield {}.".format(obj.name))
                return
        else:
            if all(s.startswith('wield') for s in obj.db.slots):
                caller.msg("You can't wear {}.".format(obj.name))
                return

        # equip primary and secondary hands with the proper feedback
        if any(s.startswith('wield') for s in obj.db.slots):
            action = 'wield'
        else:
            action = 'wear'

        if not obj.access(caller, 'equip'):
            caller.msg("You can't equip {}.".format(obj.name))
            return

        if obj in caller.equip:
            caller.msg("You're already {}ing {}.".format(action,
                                                         obj.name))
            return

        if not caller.equip.add(obj):
            string = "You can't equip {}.".format(obj.name)
            if any(caller.get(s) for s in obj.db.slots):
                string += " You already have something there."
            caller.msg(string)
            return

        # call hook
        if hasattr(obj, "at_equip"):
            obj.at_equip(caller)

        caller.msg("You {} {}.".format(action, obj))
        caller.location.msg_contents(
            "{} {}s {}.".format(caller.name.capitalize(),
                                action,
                                obj.name),
            exclude=caller)


class CmdWield(MuxCommand):
    """
    wield an item

    Usage:
      wield <obj>

    Equips a weapon or shield from your inventory to an available
    "wield" equipment slot on your character.
    """
    key = "wield"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wield what?")
            return

        caller.execute_cmd("wear {}".format(args), wield=True)


class CmdRemove(MuxCommand):
    """
    remove item

    Usage:
      remove <obj>

    Remove an equipped object and return it to your inventory.
    """
    key = "remove"
    aliases = ["rem"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Remove what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        if obj not in caller.equip:
            caller.msg("You do not have {} equipped.".format(obj.name))
            return

        if not caller.equip.remove(obj):
            return

        # call hook
        if hasattr(obj, "at_remove"):
            obj.at_remove(caller)

        caller.msg("You remove {}.".format(obj.name))
        caller.location.msg_contents(
            "{} removes {}.".format(caller.name.capitalize(),
                                    obj.name),
            exclude=caller)

