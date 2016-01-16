"""
Item and equipment-related command module.
"""
from evennia import CmdSet
from evennia.utils import fill
from commands.command import Command, MuxCommand
from evennia.utils.evtable import EvTable, fill
from typeclasses.weapons import Weapon
from typeclasses.armors import Armor, Shield


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
            data = [[],[],[]]
            for item in items:
                data[0].append("|C{}|n".format(item.name))
                data[1].append(fill(item.db.desc or "", 50))
                stat = " "
                if item.attributes.has('damage'):
                    stat += "(|rDamage: {:>2d}|n) ".format(item.db.damage)
                if item.attributes.has('range'):
                    stat += "(|GRange: {:>2d}|n) ".format(item.db.range)
                if item.attributes.has('toughness'):
                    stat += "(|yToughness: {:>2d}|n)".format(item.db.toughness)
                data[2].append(stat)
            table = EvTable(header=False, table=data, border=None, valign='t')
            string = "|YYou are carrying:|n\n{}".format(table)
        self.caller.msg(string)


class CmdEquip(MuxCommand):
    """
    view equipment

    Usage:
      equip[/swap] [<item>]

    Switches:
      s[wap] - replaces any currently equipped item

    Equips an item to its required slot(s). If no item
    specified, lists your current equipment.
    """
    key = "equip"
    aliases = ["eq"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        swap = any(s.startswith('s') for s in self.switches)
        
        if hasattr(self, "item"):
            obj = self.item
            del self.item
        else:
            obj = caller.search(args) if args else None

        if obj:
            if hasattr(self, "action"):
                action = self.action
                del self.action
            else:
                if any(isinstance(obj, i) for i in (Weapon, Shield)):
                    action = 'wield'
                elif isinstance(obj, Armor):
                    action = 'wear'
                else:
                    caller.msg("You can't equip {}.".format(obj.name))

            if obj not in caller.contents:
                caller.msg(
                    "You don't have {} in your inventory.".format(obj.name))
                return

            if not obj.access(caller, 'equip'):
                caller.msg("You can't {} {}.".format(action,
                                                     obj.name))
                return

            if obj in caller.equip:
                caller.msg("You're already {}ing {}.".format(action,
                                                             obj.name))
                return

            # check whether slots are occupied
            occupied_slots = [caller.equip.get(s) for s in obj.db.slots
                              if caller.equip.get(s)]
            if obj.db.multi_slot:
                if len(occupied_slots) > 0:
                    if swap:
                        for item in occupied_slots:
                            caller.equip.remove(item)
                    else:
                        caller.msg("You can't {} {}. ".format(action,
                                                              obj.name) +
                                   "You already have something there.")
                        return
            else:
                if len(occupied_slots) == len(obj.db.slots):
                    if swap:
                        caller.equip.remove(occupied_slots[0])
                    else:
                        caller.msg("You can't {} {}. ".format(action,
                                                              obj.name) +
                                   "You have no open {} slot{}.".format(
                                       ", or ".join(obj.db.slots),
                                       "s" if len(obj.db.slots) != 1 else ""
                                   ))
                        return

            if not caller.equip.add(obj):
                caller.msg("You can't {} {}.".format(action, obj.name))
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
        else:
            # no arguments; display current equip
            data = []
            s_width = max(len(s) for s in caller.equip.slots)
            for slot, item in caller.equip:
                if not item or not item.access(caller, 'view'):
                    continue
                stat = " "
                if item.attributes.has('damage'):
                    stat += "(|rDamage: {:>2d}|n) ".format(item.db.damage)
                if item.attributes.has('range'):
                    stat += "(|GRange: {:>2d}|n) ".format(item.db.range)
                if item.attributes.has('toughness'):
                    stat += "(|yToughness: {:>2d}|n)".format(item.db.toughness)

                data.append(
                    "  |b{slot:>{swidth}.{swidth}}|n: {item:<20.20} {stat}".format(
                        slot=slot.capitalize(),
                        swidth=s_width,
                        item=item.name,
                        stat=stat,
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
      wear[/swap] <item>

    Switches:
      s[wap] - replaces any currently equipped item

    Equips a set of armor from your inventory to an available armor
    equipment slot on your character.
    """
    key = "wear"
    locks = "cmd:all()"
    wield = False

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wear what?")
            return

        # this will search for a target
        obj = caller.search(args)

        if not obj:
            return

        elif obj.is_typeclass(Armor, exact=True):
            sw = ("/{}".format("/".join(self.switches))
                  if self.switches else "")

            caller.execute_cmd('equip',
                               args=' '.join((sw, args)),
                               item=obj,
                               action='wear')

        else:
            caller.msg("You can't wear {}.".format(obj.name))


class CmdWield(MuxCommand):
    """
    wield an item

    Usage:
      wield[/swap] <item>

    Switches:
      s[wap] - replaces any currently equipped item

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

        obj = caller.search(args)
        if not obj:
            return
        elif any(obj.is_typeclass(i, exact=False) for i in (Weapon, Shield)):
            sw = ("/{}".format("/".join(self.switches))
                  if self.switches else "")

            caller.execute_cmd('equip',
                               args=' '.join((sw, args)),
                               item=obj,
                               action='wield')
        else:
            caller.msg("You can't wield {}.".format(obj.name))


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

