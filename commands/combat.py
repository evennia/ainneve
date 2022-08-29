"""
Combat commands.
"""

from evennia import default_cmds, CmdSet, create_script
from evennia.contrib.rpg.rpsystem import CmdEmote, CmdPose, CmdSay
from evennia.utils.utils import inherits_from
from evennia.utils.evtable import EvTable
from commands.equip import CmdInventory
from commands.command import Command
from world.combat import CombatHandler

from random import choice

class CmdInitiateCombat(Command):
    """Engage an opponent in combat."""
    key = "attack"
    aliases = ("engage",)
    
    def func(self):
        caller = self.caller
        args = self.args

        target = caller.search(args)
        if not target:
            return

        # get or make combat instance
        combat = caller.ndb.combat
        if not combat:
            combat = target.ndb.combat
        elif combat != target.ndb.combat:
            # TODO: merge combat instances
            caller.msg("Merging combat instances isn't implemented yet.")
            return
        if not combat:
            combat = CombatHandler(caller, target)
        range = combat.get_range(caller, target)
        caller.msg(f"You prepare for combat! {target.get_display_name(caller)} is at {range} range.")

        # TODO: trigger combat prompt


class CmdAdvance(Command):
    """Advance towards a target."""
    key = "advance"
    aliases = ("approach",)
    locks = "cmd:in_combat()"
    
    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("combat_move"):
            caller.msg(f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds.")
            return
        
        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        if combat.advance(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add("combat_move",3)
            range = combat.get_range(caller, target)
            caller.location.msg_contents("{attacker} advances towards {target}.", exclude=caller, mapping={ "attacker": caller, "target": target })
            caller.msg(f"You advance towards {target.get_display_name(caller)} and are now at {range} range.")
        else:
            caller.msg(f"You can't advance any further towards {target.get_display_name(caller)}.")

        # TODO: trigger combat prompt


class CmdRetreat(Command):
    """Move away from a target."""
    key = "retreat"
    locks = "cmd:in_combat()"
    
    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("combat_move"):
            caller.msg(f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds.")
            return
        
        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        if combat.retreat(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add("combat_move",3)
            range = combat.get_range(caller, target)
            caller.location.msg_contents("{attacker} retreats from {target}.", exclude=caller, mapping={ "attacker": caller, "target": target })
            caller.msg(f"You retreat from {target.get_display_name(caller)} and are now at {range} range.")
        else:
            caller.msg(f"You can't retreat any further from {target.get_display_name(caller)}.")

        # TODO: trigger combat prompt


class CmdHit(Command):
    """Basic melee combat attack."""
    key = "hit"
    locks = "cmd:in_combat() and melee_equipped() and in_range(melee)"

    def func(self):
        caller = self.caller
        args = self.args
        range = "melee"

        if not caller.cooldowns.ready("attack"):
            caller.msg(f"You can't attack for {caller.cooldowns.time_left('attack',use_int=True)} more seconds.")
            return

        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        hittable = combat.in_range(caller, target, range)
        if hittable is None:
            caller.msg("You can't fight that.")
            return
        elif not hittable:
            caller.msg(f"{target.get_display_name(caller)} is too far away.")
            return

        # TODO: better handling of dual-wielding
        weapon = caller.equip.get("wield1") or caller.equip.get("wield2")
        dmg, cooldown = weapon.at_attack(caller, range)
        
        if not dmg:
            caller.msg(f"You can't hit {target.get_display_name(caller)} with your {weapon.get_display_name(caller)}.")
            return
        
        # apply damage and set cooldown
        caller.cooldowns.add("attack", cooldown)
        # TODO: add a damage check/application hook to characters and call here
        caller.msg("This is where you would do the attack stuff if it was implemented.")

        # TODO: trigger combat prompt


class CmdShoot(Command):
    """Basic ranged combat attack."""
    key = "shoot"
    locks = "cmd:in_combat() and ranged_equipped() and in_range(ranged)"

    def func(self):
        caller = self.caller
        args = self.args
        range = "ranged"

        if not caller.cooldowns.ready("attack"):
            caller.msg(f"You can't attack for {caller.cooldowns.time_left('attack',use_int=True)} more seconds.")
            return

        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        shootable = combat.in_range(caller, target, range)
        if shootable is None:
            caller.msg("You can't fight that.")
            return
        elif not shootable:
            caller.msg(f"{target.get_display_name(caller)} is too far away.")
            return

        # TODO: better handling of dual-wielding
        weapon = caller.equip.get("wield1") or caller.equip.get("wield2")
        dmg, cooldown = weapon.at_attack(caller, range)
        
        if not dmg:
            caller.msg(f"You can't shoot {target.get_display_name(caller)} with your {weapon.get_display_name(caller)}.")
            return
        
        # apply damage and set cooldown
        caller.cooldowns.add("attack", cooldown)
        # TODO: add a damage check/application hook to characters and call here
        caller.msg("This is where you would do the attack stuff if it was implemented.")

        # TODO: trigger combat prompt


class CmdFlee(Command):
    """Command to disengage and escape from combat."""
    key = "flee"
    aliases = ("escape",)
    locks = "cmd:in_combat()"
    
    def func(self):
        caller = self.caller
        args = self.args
        
        if not caller.cooldowns.ready("combat_move"):
            caller.msg(f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds.")
            return
        
        exits = [ex for ex in caller.location.contents if ex.destination]
        if not exits:
            caller.msg("There's nowhere to run!")
            return

        # TODO: add checks for flight success, e.g. `caller.at_pre_flee`

        # this is the actual fleeing bit
        caller.msg("You flee!")
        caller.ndb.combat.remove(caller)
        target = choice(exits)
        # using execute_cmd instead of duplicating all the checks in ExitCommand
        caller.execute_cmd(target.key)


class CombatCmdSet(CmdSet):
    """Command set containing combat commands"""
    key = "combat_cmdset"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdInitiateCombat())
        self.add(CmdHit())
        self.add(CmdShoot())
        self.add(CmdAdvance())
        self.add(CmdRetreat())
        self.add(CmdFlee())
