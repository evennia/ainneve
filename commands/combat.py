"""
Combat commands.
"""

from random import choice

from evennia import CmdSet
from evennia.utils import inherits_from
from world.combat import CombatHandler
from world.enums import CombatRange
from .command import Command


class CombatCommand(Command):
    cooldown_key = ""
    cooldown_message = "You can't do that for another {delay} seconds."

    in_combat_only = True
    requires_target = True

    def __init__(self, **kwargs):
        self.target = None  # This line is to avoid the IDE complaints
        super().__init__(**kwargs)

    def parse(self):
        super().parse()
        self.target = self.get_target()

    def get_target(self):
        return self.caller.search(self.args)

    def validate(self) -> bool:
        if self.requires_target and not self._validate_target():
            return False

        if not self._validate_cooldown():
            return False

        return True

    def _validate_target(self) -> bool:
        """
        Make sure the target is something that can be attacked
        """
        target = self.target
        if not target or not target.dbid:
            return False

        if not self._validate_target_can_be_attacked(target):
            return False

        if not self._validate_target_is_mob_or_pvp_allowed(target):
            return False

        if self.in_combat_only:
            if not self._validate_target_is_in_combat_with(target):
                return False

        return True

    def _validate_target_can_be_attacked(self, target) -> bool:
        if not inherits_from(target, "typeclasses.characters.BaseCharacter"):
            self.caller.msg("You can't attack that.")
            return False

        return True

    def _validate_target_is_mob_or_pvp_allowed(self, target) -> bool:
        if target.is_pc and not target.location.allow_pvp:
            self.caller.msg("You can't attack another player here.")
            return False

        return True

    def _validate_target_is_in_combat_with(self, target) -> bool:
        if not target.nattributes.has("combat"):
            caller = self.caller
            caller.msg(f"You aren't in combat with {target.get_display_name(caller)}.")
            return False
        return True

    def _validate_cooldown(self) -> bool:
        cooldown_key = self.cooldown_key
        if not cooldown_key:
            return True

        caller = self.caller
        if not caller.cooldowns.ready(cooldown_key):
            delay = caller.cooldowns.time_left(cooldown_key, use_int=True)
            msg = self.cooldown_message.format(delay=delay)
            caller.msg(msg)
            return False

        return True


class CmdInitiateCombat(CombatCommand):
    """Engage an opponent in combat."""

    key = "attack"
    aliases = ("engage", "kill")

    in_combat_only = False

    def func(self):
        caller = self.caller
        target = self.target
        if not self.validate():
            return

        combat = CombatHandler.get_or_create(caller, target)
        combat_range = combat.get_range(caller, target)
        caller.msg(
            f"You prepare for combat! {target.get_display_name(caller)} is at {combat_range.name.lower()} range."
        )

        # TODO: trigger combat prompt


class CmdAdvance(CombatCommand):
    """Advance towards a target."""

    key = "advance"
    aliases = ("approach",)
    locks = "cmd:in_combat()"

    cooldown_key = "combat_move"
    cooldown_message = "You can't move for another {delay} seconds."

    def func(self):
        caller = self.caller
        target = self.target
        if not self.validate():
            return

        combat: CombatHandler = caller.ndb.combat
        if combat.approach(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add(self.cooldown_key, 3)
            combat_range = combat.get_range(caller, target)
            caller.location.msg_contents(
                "{attacker} advances towards {target}.",
                exclude=caller,
                mapping={"attacker": caller, "target": target},
            )
            caller.msg(
                f"You advance towards {target.get_display_name(caller)} and are now at {combat_range.lower()} range."
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

    cooldown_key = "combat_move"
    cooldown_message = "You can't move for another {delay} seconds."

    def func(self):
        caller = self.caller
        target = self.target
        if not self.validate():
            return

        combat = caller.ndb.combat
        if combat.retreat(caller, target):
            # TODO: base movement cooldown on character stats
            caller.cooldowns.add(self.cooldown_key, 3)
            combat_range = combat.get_range(caller, target)
            caller.location.msg_contents(
                "{attacker} retreats from {target}.",
                exclude=caller,
                mapping={"attacker": caller, "target": target},
            )
            caller.msg(
                f"You retreat from {target.get_display_name(caller)} and are now at {combat_range.lower()} range."
            )
        else:
            caller.msg(
                f"You can't retreat any further from {target.get_display_name(caller)}."
            )

        # TODO: trigger combat prompt


class CmdHit(CombatCommand):
    """
    Basic melee combat attack.

    hit <target>
    """

    key = "hit"
    locks = "cmd:in_combat() and melee_equipped()"

    cooldown_key = "attack"
    cooldown_message = "You can't attack for {delay} more seconds."

    def func(self):
        caller = self.caller
        target = self.target
        if not self.validate():
            return

        combat: CombatHandler = caller.ndb.combat
        hittable = combat.in_range(caller, target, CombatRange.MELEE)
        if hittable is None:
            caller.msg("You can't fight that.")
            return
        elif not hittable:
            caller.msg(f"{target.get_display_name(caller)} is too far away.")
            return

        combat.at_melee_attack(caller, target)

    def validate(self) -> bool:
        result = super().validate()
        if not result:
            return result

        if not self._validate_stamina_cost():
            return False

        return True

    def _validate_stamina_cost(self) -> bool:
        caller = self.caller
        combat = caller.ndb.combat
        base_cost = 2
        if caller.weapon:
            base_cost = caller.weapon.stamina_cost

        stamina_cost = combat.calc_attack_stamina_cost(caller, CombatRange.MELEE, base_cost)
        if stamina_cost >= caller.stamina:
            caller.msg("You are too exhausted!")
            return False

        return True


class CmdShoot(CombatCommand):
    """Basic ranged combat attack."""

    key = "shoot"
    locks = "cmd:in_combat() and ranged_equipped()"

    cooldown_key = "attack"
    cooldown_message = "You can't attack for {delay} more seconds."

    def func(self):
        caller = self.caller
        target = self.target
        if not self.validate():
            return

        combat: CombatHandler = caller.ndb.combat
        shootable = combat.in_range(caller, target, CombatRange.RANGED)
        if shootable is None:
            caller.msg("You can't fight that.")
            return
        elif not shootable:
            caller.msg(f"{target.get_display_name(caller)} is too far away.")
            return
        #elif too_close:
        #    caller.msg(f"{target.get_display_name(caller)} is too close.")
        #    return

        combat.at_ranged_attack(caller, target)


class CmdFlee(CombatCommand):
    """Command to disengage and escape from combat."""

    key = "flee"
    aliases = ("escape",)
    locks = "cmd:in_combat()"

    cooldown_key = "combat_move"
    cooldown_message = "You can't move for another {delay} seconds."
    requires_target = False

    def func(self):
        caller = self.caller
        self.validate()

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

    def get_target(self):
        return None


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
