"""
Combat commands.
"""

from random import choice
from evennia import CmdSet
from evennia.utils import inherits_from

from world.combat import CombatHandler

from .command import Command


class CombatCommand(Command):
    def get_valid_target(self, in_combat=True):
        """
        Make sure the target is something that can be attacked
        """
        if target := self.caller.search(self.args):
            if not inherits_from(target, "typeclasses.characters.BaseCharacter"):
                self.caller.msg("You can't attack that.")
                return None
            if target.is_pc and not target.location.allow_pvp:
                self.caller.msg("You can't attack another player here.")
                return None
            if in_combat:
                if not target.nattributes.has("combat"):
                    self.caller.msg(
                        f"You aren't in combat with {target.get_display_name(self.caller)}."
                    )
                    return None
            return target
        else:
            return None


class CmdInitiateCombat(CombatCommand):
    """Engage an opponent in combat."""

    key = "attack"
    aliases = ("engage",)

    def func(self):
        caller = self.caller

        target = self.get_valid_target(in_combat=False)
        if not target:
            return

        # get or make combat instance
        combat = caller.ndb.combat
        if not combat:
            # caller is not in combat, so use the target's combat instance
            combat = target.ndb.combat
        if not combat:
            # still no combat instance means neither are in combat; start new instance
            combat = CombatHandler(caller, target)
        elif combat != target.ndb.combat:
            # both parties are in separate combat instances; combine into one
            combat.merge(target.ndb.combat)
        range = combat.get_range(caller, target)
        caller.msg(
            f"You prepare for combat! {target.get_display_name(caller)} is at {range.lower()} range."
        )

        # TODO: trigger combat prompt


class CmdAdvance(CombatCommand):
    """Advance towards a target."""

    key = "advance"
    aliases = ("approach",)
    locks = "cmd:in_combat()"

    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("combat_move"):
            caller.msg(
                f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds."
            )
            return

        combat = caller.ndb.combat
        if combat.advance(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add("combat_move", 3)
            range = combat.get_range(caller, target)
            caller.location.msg_contents(
                "{attacker} advances towards {target}.",
                exclude=caller,
                mapping={"attacker": caller, "target": target},
            )
            caller.msg(
                f"You advance towards {target.get_display_name(caller)} and are now at {range.lower()} range."
            )
        else:
            caller.msg(
                f"You can't advance any further towards {target.get_display_name(caller)}."
            )

        # TODO: trigger combat prompt


class CmdRetreat(CombatCommand):
    """Move away from a target."""

    key = "retreat"
    locks = "cmd:in_combat()"

    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("combat_move"):
            caller.msg(
                f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds."
            )
            return

        target = caller.search(args)
        if not target:
            return

        combat = caller.ndb.combat
        if combat.retreat(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add("combat_move", 3)
            range = combat.get_range(caller, target)
            caller.location.msg_contents(
                "{attacker} retreats from {target}.",
                exclude=caller,
                mapping={"attacker": caller, "target": target},
            )
            caller.msg(
                f"You retreat from {target.get_display_name(caller)} and are now at {range.lower()} range."
            )
        else:
            caller.msg(
                f"You can't retreat any further from {target.get_display_name(caller)}."
            )

        # TODO: trigger combat prompt


class CmdHit(CombatCommand):
    """Basic melee combat attack."""

    key = "hit"
    locks = "cmd:in_combat() and melee_equipped()"

    def func(self):
        caller = self.caller
        args = self.args
        range = "MELEE"

        if not caller.cooldowns.ready("attack"):
            caller.msg(
                f"You can't attack for {caller.cooldowns.time_left('attack',use_int=True)} more seconds."
            )
            return

        target = self.get_valid_target()
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

        weapon = caller.weapon
        # TODO: calculate damage, delay
        dmg = 1
        cooldown = 5

        if not dmg:
            caller.msg(
                f"You can't hit {target.get_display_name(caller)} with your {weapon.get_display_name(caller)}."
            )
            return

        # apply damage and set cooldown
        caller.cooldowns.add("attack", cooldown)

        # TODO: add a damage/block check/application hook to BaseCharacter and call here

        caller.location.msg_contents(
            f"$You() $conj(hit) {{{target.key}}} with $pron(your) {{{weapon.key}}} for {dmg} damage.",
            mapping={target.key: target, weapon.key: weapon},
            from_obj=caller,
        )
        target.at_damage(dmg, attacker=caller)

        # TODO: trigger combat prompt


class CmdShoot(CombatCommand):
    """Basic ranged combat attack."""

    key = "shoot"
    locks = "cmd:in_combat() and ranged_equipped()"

    def func(self):
        caller = self.caller
        args = self.args
        range = "RANGED"

        if not caller.cooldowns.ready("attack"):
            caller.msg(
                f"You can't attack for {caller.cooldowns.time_left('attack',use_int=True)} more seconds."
            )
            return

        target = self.get_valid_target()
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

        weapon = caller.weapon
        # TODO: calculate damage, delay
        dmg = 1
        cooldown = 5

        if not dmg:
            caller.msg(
                f"You can't shoot {target.get_display_name(caller)} with your {weapon.get_display_name(caller)}."
            )
            return

        # apply damage and set cooldown
        caller.cooldowns.add("attack", cooldown)

        # TODO: add a damage/block check/application hook to BaseCharacter and call here

        caller.location.msg_contents(
            f"$You() $conj(shoot) {{{target.key}}} with $pron(your) {{{weapon.key}}} for {dmg} damage.",
            mapping={target.key: target, weapon.key: weapon},
            from_obj=caller,
        )
        target.at_damage(dmg, attacker=caller)

        # TODO: trigger combat prompt


class CmdFlee(CombatCommand):
    """Command to disengage and escape from combat."""

    key = "flee"
    aliases = ("escape",)
    locks = "cmd:in_combat()"

    def func(self):
        caller = self.caller
        args = self.args

        if not caller.cooldowns.ready("combat_move"):
            caller.msg(
                f"You can't move for another {caller.cooldowns.time_left('combat_move',use_int=True)} seconds."
            )
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


# TODO: add defend command for changing/setting your defense zone


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
