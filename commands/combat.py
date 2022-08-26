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


class InitCombatCmdSet(CmdSet):
    """Command set containing combat starting commands"""
    key = 'combat_init_cmdset'
    priority = 1
    mergetype = 'Union'

    def at_cmdset_creation(self):
        self.add(CmdInitiateAttack())


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
            # merge combat instances
            caller.msg("Merging combat instances isn't implemented yet.")
            return
        if not combat:
            combat = CombatHandler(caller, target)
        range = combat.get_range(caller, target)
        caller.msg(f"You prepare for combat! {target.get_display_name(caller)} is within {range} weapon range.")

class CmdAdvance(Command):
    """Advance towards a target."""
    key = "advance"
    aliases = ("approach",)
    locks = "cmd:in_combat()"
    
    def func(self):
        caller = self.caller
        args = self.args
        # should do movement cooldown check here, actually
        
        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        success = combat.advance(caller, target)
        if success:
            # apply movement cost/cooldown here
            range = combat.get_range(caller, target)
            caller.location.msg_contents("{attacker} advances towards {target}.", exclude=caller, mapping={ "attacker": caller, "target": target })
            caller.msg(f"You advance towards {target.get_display_name(caller)} and are now in {range} weapon range.")
        else:
            caller.msg(f"You can't advance any further towards {target.get_display_name(caller)}.")

        combat.prompt(caller)

class CmdRetreat(Command):
    """Move away from a target."""
    key = "retreat"
    locks = "cmd:in_combat()"
    
    def func(self):
        caller = self.caller
        args = self.args
        # should do movement cooldown check here, actually
        
        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        success = combat.retreat(caller, target)
        if success:
            # apply movement cost/cooldown here
            range = combat.get_range(caller, target)
            caller.location.msg_contents("{attacker} retreats from {target}.", exclude=caller, mapping={ "attacker": caller, "target": target })
            caller.msg(f"You retreat from {target.get_display_name(caller)} and are now in {range} weapon range.")
        else:
            caller.msg(f"You can't retreat any further from {target.get_display_name(caller)}.")

        combat.prompt(caller)


class CmdHit(Command):
    """Basic melee combat attack."""
    key = "hit"
    locks = "cmd:in_combat() and melee_equipped() and in_range(melee)"

    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("attack"):
            # include a time here
            caller.msg("You can't attack again yet.")
            return

        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        range = combat.get_range(caller, target)
        if not range:
            caller.msg("You can't fight that.")
            return

        if range != "melee":
            caller.msg(f"{target.get_display_name(caller)} is too far away.")
            return

        # check equip handler to find how to get wielded weapon 
        dmg, cooldown = weapon.at_attack(caller, range)
        
        if not dmg:
            caller.msg(f"You can't hit {target.get_display_name(caller)} from here.")
            return
        
        # apply damage and set cooldown
				caller.cooldowns.add("attack", cooldown)
        caller.msg("This is where you would do the attack stuff if it was implemented.")


class CmdShoot(Command):
    """Basic ranged combat attack."""
    key = "shoot"
    locks = "cmd:in_combat() and ranged_equipped() and in_range(ranged)"

    def func(self):
        caller = self.caller
        args = self.args

        # haven't actually added cooldowns yet
        if not caller.cooldowns.ready("attack"):
            # include a time here
            caller.msg("You can't attack again yet.")
            return

        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        range = combat.get_range(caller, target)
        if not range:
            caller.msg("You can't fight that.")
            return

        # check equip handler to find how to get wielded weapon 
        dmg, cooldown = weapon.at_attack(caller, range)
        
        if not dmg:
            caller.msg(f"You can't hit {target.get_display_name(caller)} from here.")
            return
        
        # apply damage and set cooldown
				caller.cooldowns.add("attack", cooldown)
        caller.msg("This is where you would do the attack stuff if it was implemented.")


class CombatCmdSet(CmdSet):
    """Command set containing combat commands"""
    key = "combat_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdActionList())
        self.add(CmdCancelAction())
        self.add(CmdDropItem())
        self.add(CmdGetItem())
        self.add(CmdEquip())
        self.add(CmdKick())
        self.add(CmdStrike())
        self.add(CmdDodge())
        self.add(CmdAdvance())
        self.add(CmdRetreat())
        self.add(CmdFlee())
        # self.add(CmdWrestle())
        # self.add(CmdTackle())
