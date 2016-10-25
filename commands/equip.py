"""
Item and equipment-related command module.
"""
from evennia import CmdSet
from commands.command import MuxCommand
from evennia.utils.evtable import EvTable, fill
from typeclasses.weapons import Weapon
from typeclasses.armors import Armor, Shield


__all__ = ('CmdInventory', 'CmdEquip',
           'CmdWear', 'CmdWield', 'CmdRemove')


_INVENTORY_ERRMSG = "You don't have '{}' in your inventory."
_EQUIP_ERRMSG = "You do not have '{}' equipped."

class EquipCmdSet(CmdSet):
    """CmdSet for item / equip commands."""
    key = "equip_cmdset"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdInventory())
        self.add(CmdEquip())
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
    equip equipment.

    Usage:
      equip[/swap] <equippable item>
      wear[/swap] <wearable item>
      wield[/swap] <wieldable item>
    Switches:
      s[wap] - replaces any currently equipped item

    Equips an item to its required slot(s). If no item or unusable items
    specified, lists the items in your inventory available to be
    equipped/worn/wielded.
    """
    """
    Authors Note:
    This is a heavily modified version of Nadorrano's equipment commands.
    This equipment command uses a dictionary of alias's and typeclasses to
    ensure that only certain typeclasses are equippable by certain aliases.
    E.G.    The command "wear" only works for Armor types.
            The command "wield" only works for Weapon and Shield types.

    This is easily exapandable by altering the dictionary below with any
    additional keys, aliases or typeclasses.
    """
    key = "equip"
    aliases = ["eq", "wear", "wield"]
    locks = "cmd:all()"
    keymatrix = {
        ("equip", "eq"): ("equip", [Armor, Weapon, Shield]),
        ("wear"): ("wear", [Armor]),
        ("wield"): ("wield", [Weapon, Shield]),
    }

    def _display_item_list(self, caller, typeclasses, cmd):
        """
        Returns a list of items in caller's inventory that can be equipped by
        the cmd specified.
        """
        # Create list of inventory items of right typeclass and not equiped.
        available = [i for i in caller.contents
                     if any(isinstance(i, typeclass) for typeclass in typeclasses)
                     and i not in caller.equip]
        # Message caller with table of options or message that nothing matches.
        if len(available) <= 0:
            output = "You have nothing to {} in your inventory".format(cmd)
        else:
            data = [[], [], []]
            for item in available:
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
            output = "|wYou can {}:|n\n{}".format(cmd, table)
        caller.msg(output)
        return

    def func(self):
        """
        equips item
        """

        # Set up function variables.
        caller = self.caller
        cmd = self.cmdstring
        typeclasses = []
        swap = any(strings.startswith('s') for strings in self.switches)
        args = self.args.strip()

        # Convert cmd into appropriate action word to be used in player msgs.
        # I.e. cmd = "eq" -> cmd = "equip"
        for key in self.keymatrix:
            if cmd in key:
                cmd = self.keymatrix[key][0]
                typeclasses = self.keymatrix[key][1]

        # If no arguments, display all items that correspond to that command.
        if not args:
            caller.msg("{} what?".format(cmd.capitalize()))
            self._display_item_list(caller, typeclasses, cmd)
            return

        # Handle if there are arguments.
        # Search for target object, giving error message if it cannot be found.
        obj = caller.search(args,
                            candidates=caller.contents,
                            nofound_string=_INVENTORY_ERRMSG.format(
                                args))
        if not obj:
            # If no object found, display available items after err msg.
            self._display_item_list(caller, typeclasses, cmd)
            return

        # Check obj is of allowed typeclass for command used.
        matches = (isinstance(obj, typeclass) for typeclass in typeclasses)
        if not any(matches):
            caller.msg("You can't {} {}.".format(cmd, obj.name))
            return

        # Check if obj has correct permission.
        if not obj.access(caller, 'equip'):
            caller.msg("You can't {} {}.".format(cmd, obj.name))
            return

        # Check if target is already equipped.
        if obj in caller.equip:
            caller.msg(
                "You're already {}ing {}.".format(cmd, obj.name))
            return

        # Check whether slots required are occupied
        # Creates list of slots required that are occupied.
        occupied_slots = [caller.equip.get(item) for item in
                          obj.db.slots
                          if caller.equip.get(item)]

        # Code for multi_slot items. If not all slots available.
        if obj.db.multi_slot:
            if len(occupied_slots) > 0:
                # If swap switch, remove items in all req slots.
                if swap:
                    for item in occupied_slots:
                        caller.equip.remove(item)
                # If no switch abort command.
                else:
                    caller.msg("You can't {} {}. ".format(cmd, obj.name) +
                               "You already have something there.")
                    return

        # Code for single slot.
        else:
            if len(occupied_slots) == len(obj.db.slots):
                # If swap switch, remove item.
                if swap:
                    caller.equip.remove(occupied_slots[0])
                # If no swap switch, abort command.
                else:
                    caller.msg("You can't {} {}. ".format(cmd, obj.name) +
                               "You have no open {} slot{}.".format(
                                   ", or ".join(obj.db.slots),
                                   "s" if len(obj.db.slots) != 1 else ""
                               ))
                    return

        # This is where the work occurs. Because the add command
        # returns True or False on success it is wrapped in an if
        # supplying a message if it fails.
        if not caller.equip.add(obj):
            caller.msg("You can't {} {}.".format(cmd, obj.name))
            return

        # call hook
        if hasattr(obj, "at_equip"):
            obj.at_equip(caller)

        caller.msg("You {} {}.".format(cmd, obj))
        caller.location.msg_contents(
            "{} {}s {}.".format(caller.name.capitalize(), cmd,
                                obj.name), exclude=caller)


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

        # search for target in our equip
        equipped_items = [i[1] for i in caller.equip if i[1]]
        obj = caller.search(
            args,
            candidates=equipped_items,
            nofound_string=_EQUIP_ERRMSG.format(args))

        if not obj:
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
