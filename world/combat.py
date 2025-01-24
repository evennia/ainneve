import random
from random import randrange
from typing import Self, TYPE_CHECKING

from .enums import CombatRange, AttackType


if TYPE_CHECKING:
    from typeclasses.characters import BaseCharacter
    from typeclasses.objects import WeaponObject

_MAX_RANGE = max([en.value for en in CombatRange])

# format for combat prompt, currently unused
# health, mana, current attack cooldown
COMBAT_PROMPT = "HP {hp} - MP {mana} - SP {stamina}"


class CombatRules:
    __slots__ = ("handler",)

    def __init__(self, handler: 'CombatHandler'):
        self.handler = handler

    def validate_melee_attack(self, attacker: 'BaseCharacter', target: 'BaseCharacter', weapon: 'WeaponObject | None' = None) -> bool:
        if not attacker.combat:
            attacker.msg("You are not in combat.")
            return False

        if not target.combat or target.combat != attacker.combat:
            attacker.msg("They are not in combat with you.")
            return False

        if target.is_pc and not (target.location and target.location.allow_pvp):
            attacker.msg("You can't attack another player here.")
            return False

        if not attacker.cooldowns.ready("attack"):
            delay = attacker.cooldowns.time_left("attack", use_int=True)
            attacker.msg(f"You can't attack for {delay} more seconds.")
            return False

        base_cost = 2
        if weapon:
            base_cost = weapon.stamina_cost

        stamina_cost = self.get_attack_stamina_cost(attacker, AttackType.MELEE, base_cost)
        if stamina_cost >= attacker.stamina:
            attacker.msg("You are too exhausted!")
            return False

        return True

    def get_initial_position(self, fighter: 'BaseCharacter') -> CombatRange:
        # TODO Ranged fighters should start further apart
        # TODO Fighters should be grouped according to alliance at the start of a fight.
        # TODO Fighters should be added at the furthest position on their alliance's side if added during the fight.

        # Temporary code until we can implement the above
        if fighter.is_pc:
            return CombatRange.MELEE
        else:
            return CombatRange.MELEE

    @property
    def is_combat_finished(self) -> bool:
        return len(self.handler.positions) <= 1

    def get_strike_zone(self, attack_location, defense_location):
        """
        We can expand on this to include adjacent sides/etc or weightings/corners
        """
        return (attack_location == defense_location)

    def get_attack_stamina_cost(self, attacker: 'BaseCharacter', attack_type: AttackType, base_cost: int) -> int:
        if attacker.aggro == "aggressive":
            cost = int(base_cost * 1.5)
        elif attacker.aggro == "defensive":
            cost = int(base_cost / 2)
        else:
            cost = base_cost

        return cost

    def get_defense_stamina_cost(self, attacker: 'BaseCharacter', attack_type: AttackType, base_cost: int, target: 'BaseCharacter') -> int:
        return 2  # TODO FIXME update this

    def roll(self, roller: 'BaseCharacter', target: 'BaseCharacter', stat: str, is_dodge: bool = False) -> int:
        """
        Roll 2d6 + roller's stat +/- roller's aggression + applicable bonuses
        """
        roll = randrange(1,6) + randrange(1,6)
        roll += roller.attributes.get(stat, 0)

        if is_dodge:
            if roller.aggro == "aggressive":
                roll += -1
            elif roller.aggro == "defensive":
                roll +=  1
        else:
            if roller.aggro == "aggressive":
                roll +=  1
            elif roller.aggro == "defensive":
                roll += -1

        # TODO FIXME Add any bonuses this roller has versus the given target
        roll += 0

        return roll


class CombatHandler:
    __slots__ = ('positions', 'rules')

    rules_class = CombatRules

    def __init__(self, attacker: 'BaseCharacter', target: 'BaseCharacter', custom_rules: type(CombatRules) | None = None):
        self.rules = custom_rules(self) if custom_rules else self.rules_class(self)
        self.positions: dict['BaseCharacter', CombatRange] = {}
        self.add(attacker)
        self.add(target)

    @classmethod
    def get_or_create(cls, attacker, target) -> Self:
        """
        This function will create the CombatHandler or merge existing ones, then return it.
        """
        attacker_combat: Self = attacker.combat
        target_combat: Self = target.combat

        if attacker_combat and target_combat:
            attacker_combat.merge(target.combat)
            return attacker_combat

        elif attacker_combat:
            attacker_combat.add(target)
            return attacker_combat

        elif target_combat:
            target_combat.add(attacker)
            return target_combat

        else:
            return CombatHandler(attacker, target)

    def add(self, fighter: 'BaseCharacter') -> None:
        """
        Add a new combatant to the combat instance.
        """
        assert fighter not in self.positions, f"Fighter {fighter} was already added to the fight!"

        self.positions[fighter] = self.rules.get_initial_position(fighter)
        fighter.combat = self

    def remove(self, fighter: 'BaseCharacter') -> None:
        """
        Removes a fighter from the combat instance.
        """
        assert fighter in self.positions, f"Fighter {fighter} was already removed from the fight!"


        del self.positions[fighter]
        if fighter.combat == self:
            fighter.combat = None

        if self.is_finished:
            self.end_combat()


    def merge(self, other):
        """
        Merge another combat instance into this one
        """
        self.positions.update(other.positions)
        for obj in other.positions.keys():
            obj.ndb.combat = self

        other.positions = {}

    def end_combat(self) -> None:
        for fighter in self.positions:
            if fighter.combat == self:
                fighter.combat = None

            if fighter.is_pc:
                # Temporary message for debugging
                fighter.msg("You are victorious!")

        self.positions = {}

    @property
    def is_finished(self) -> bool:
        return self.rules.is_combat_finished

    def get_range(self, attacker: 'BaseCharacter', target: 'BaseCharacter') -> CombatRange:
        """
        Get the distance from target in terms of weapon range.
        """
        assert attacker in self.positions, f"Attacker {attacker} is not in combat!"
        assert target in self.positions, f"Target {target} is not in combat!"

        distance = abs(self.positions[attacker] - self.positions[target])
        for range_enum in CombatRange:
            if range_enum.value >= distance:
                return range_enum

        return CombatRange.RANGED

    def in_range(self, attacker: 'BaseCharacter', target: 'BaseCharacter', combat_range: CombatRange) -> bool:
        """Check if target is within the specified range of attacker."""
        assert attacker in self.positions, f"Attacker {attacker} is not in combat!"
        assert target in self.positions, f"Target {target} is not in combat!"

        distance = abs(self.positions[attacker] - self.positions[target])

        return distance <= combat_range

    def any_in_range(self, attacker: 'BaseCharacter', combat_range: CombatRange) -> bool:
        assert attacker in self.positions, f"Attacker {attacker} is not in combat!"

        a_pos = self.positions[attacker]

        return any(
            p
            for c, p in self.positions.items()
            if abs(a_pos - p) <= combat_range and c != attacker
        )

    def approach(self, mover: 'BaseCharacter', target: 'BaseCharacter') -> bool:
        """
        Move a combatant towards the target.
        Returns True if the distance changed, or False if it didn't.
        """
        assert mover in self.positions, f"Mover {mover} is not in combat!"
        assert target in self.positions, f"Target {target} is not in combat!"

        start = self.positions[mover]
        end = self.positions[target]

        if start == end:
            # already as close as you can get
            return False

        change = 1 if start < end else -1
        self.positions[mover] += change

        return True

    def retreat(self, mover: 'BaseCharacter', target: 'BaseCharacter') -> bool:
        """
        Move a combatant away from the target.
        Returns True if the distance changed, or False if it didn't.
        """
        assert mover in self.positions, f"Mover {mover} is not in combat!"
        assert target in self.positions, f"Target {target} is not in combat!"

        start = self.positions[mover]
        end = self.positions[target]

        # can't move beyond maximum weapon range
        if abs(start - end) >= _MAX_RANGE:
            return False

        change = -1 if start < end else 1
        self.positions[mover] += change

        return True


    def at_melee_attack(self, attacker: 'BaseCharacter', target: 'BaseCharacter') -> None:
        """
        Proceed with a melee attack.
        All validations should be done before this method.
        """
        blocked = False
        parried = False
        weapon = attacker.weapon
        range_to_target = self.get_range(attacker, target)

        # Make sure the attacker has a basic weapon, if not, default to "fist" melee weapon stats
        if weapon:
            min_damage = weapon.min_damage
            max_damage = weapon.max_damage
            stamina_cost = weapon.stamina_cost
            cooldown = weapon.cooldown
        else:
            min_damage = 1
            max_damage = 2
            stamina_cost = 2
            cooldown = 2

        attacker_stamina_cost = self.rules.get_attack_stamina_cost(attacker, AttackType.MELEE, stamina_cost)
        attacker.spend_stamina(attacker_stamina_cost)
        attacker.cooldowns.add("attack", cooldown)

        # Check to see if the target is using a shield
        #   their Block zone matches the Attacker's target zone
        if target.shield is not None:
            blocked = True

        # Check if target is wielding something that can parry,
        #    and if their Parry zone matches the Attacker's target zone.
        if target.weapon is not None and target.weapon.can_parry():
            parried = True

        if blocked or parried:
            # See if target can defend
            target_defense_stamina_cost = self.rules.get_defense_stamina_cost(
                attacker,
                AttackType.MELEE,
                stamina_cost,
                target
            )
            if target_defense_stamina_cost < target.stamina:
                target.spend_stamina(target_defense_stamina_cost)
                if range_to_target == CombatRange.MELEE:
                    attacker.cooldowns.add("attack", cooldown + 1)
                    target.buffs.add_buff("attack", 2, versus=attacker, duration=1)

                if blocked:
                    blocking_item = target.shield
                else:
                    blocking_item = target.weapon

                target.location.msg_contents(
                    "$You() $conj(block) the attack with $pron(your) {blocking_item}.",
                    mapping={"blocking_item": blocking_item},
                    from_obj=target,
                )
                return

        attack_roll = self.rules.roll(attacker, target, "strength")
        defense_roll = self.rules.roll(target, attacker, "cunning", is_dodge=True)
        if attack_roll >= defense_roll:
            damage = random.randrange(min_damage, max_damage)
            damage += attacker.strength

            # multiply the result by the Attackers Aggression factor (round up)
            if attacker.aggro == "defensive":
                damage = int(damage / 2)
            elif attacker.aggro == "aggressive":
                damage = int(damage * 1.5)

            # Subtract off the Target's armor, if any.
            if target.armor:
                damage = damage - target.armor
                if damage <= 0:
                    attacker.location.msg_contents(
                        "$pron(your) attack fails to pierce {target}'s {armor}.",
                        mapping={"target": target, "armor": target.armor},
                        from_obj=attacker,
                    )
                    return

            # apply the remainder to the Targets Health
            attacker.location.msg_contents(
                "$You() $conj(hit) {target} with $pron(your) {weapon}.",
                mapping={"target": target, "weapon": weapon or "fists"},
                from_obj=attacker,
            )
            target.at_damage(damage)

            return damage
        else:
            target.location.msg_contents(
                "$You() $conj(dodge) the attack.",
                from_obj=target,
            )

    def at_ranged_attack(self, attacker, target):
        """
        Proceed with a ranged attack.
        All validations should be done before this method.
        """

        blocked = False
        parried = False
        range_to_target = self.get_range(attacker, target)
        weapon = attacker.weapon
        min_damage = weapon.min_damage
        max_damage = weapon.max_damage
        stamina_cost = weapon.stamina_cost
        cooldown = weapon.cooldown

        attacker_stamina_cost = self.rules.get_attack_stamina_cost(attacker, AttackType.RANGED, stamina_cost)
        attacker.spend_stamina(attacker_stamina_cost)
        attacker.cooldowns.add("attack", cooldown)

        # Check to see if the target is using a shield
        #   their Block zone matches the Attacker's target zone
        if target.shield is not None:
            blocked = True

        # Check if target is wielding something that can parry,
        #    and if their Parry zone matches the Attacker's target zone.
        if target.weapon is not None and target.weapon.can_parry():
            parried = True

        if blocked or parried:
            # See if target can defend
            target_defense_stamina_cost = self.rules.get_defense_stamina_cost(
                attacker,
                AttackType.RANGED,
                stamina_cost,
                target
            )
            if target_defense_stamina_cost < target.stamina:
                target.spend_stamina(target_defense_stamina_cost)
                if range_to_target == CombatRange.MELEE:
                    attacker.cooldowns.add("attack", cooldown + 1)
                    target.add_buff("attack", 2, versus=attacker, duration=1)

                if blocked:
                    blocking_item = target.shield
                else:
                    blocking_item = target.weapon

                target.location.msg_contents(
                    "$You() $conj(block) the attack with $pron(your) {blocking_item}.",
                    mapping={"blocking_item": blocking_item},
                    from_obj=target,
                )
                return

        attack_roll = self.rules.roll(attacker, target, "cunning")
        target_size_penalty = 0
        if self.in_range(attacker, target, CombatRange.SHORT):
            range_penalty = 0
        else:
            # TODO Determine penalty
            range_penalty = 2

        defense_roll = 5 + target_size_penalty + range_penalty
        if attack_roll >= defense_roll:
            damage = random.randrange(min_damage, max_damage)
            damage += attacker.strength

            # multiply the result by the Attackers Aggression factor (round up)
            if attacker.aggro == "defensive":
                damage = int(damage / 2)
            elif attacker.aggro == "aggressive":
                damage = int(damage * 1.5)

            # Subtract off the Target's armor, if any.
            if target.armor:
                damage = damage - target.armor
                if damage <= 0:
                    attacker.location.msg_contents(
                        "$pron(your) attack fails to pierce {target}'s {armor}.",
                        mapping={"target": target, "armor": target.armor},
                        from_obj=attacker,
                    )
                    return

            # apply the remainder to the Targets Health
            attacker.location.msg_contents(
                "$You() $conj(shoot) {target} with $pron(your) {weapon}.",
                mapping={"target": target, "weapon": weapon},
                from_obj=attacker,
            )
            target.at_damage(damage)

            return damage
        else:
            target.location.msg_contents(
                "$You() $conj(dodge) the attack.",
                from_obj=target,
            )

    def at_thrown_attack(self, attacker, target):
        blocked = False
        parried = False
        range_to_target = self.get_range(attacker, target)
        weapon = attacker.weapon

        if attacker.weapon.is_throwable is not None:
            # set the Base Physical Damage Range to 1-2 and the Base Stamina Cost to 4.
            min_damage = 1
            max_damage = 2
            stamina_cost = 4
            cooldown = 4
        else:
            min_damage = weapon.min_damage
            max_damage = weapon.max_damage
            stamina_cost = weapon.stamina_cost
            cooldown = weapon.cooldown

        attacker_stamina_cost = self.rules.get_attack_stamina_cost(attacker, AttackType.THROWN, stamina_cost)
        attacker.spend_stamina(attacker_stamina_cost)
        attacker.cooldowns.add("attack", cooldown)

        # Check to see if the target is using a shield
        #   their Block zone matches the Attacker's target zone
        if target.shield is not None:
            blocked = True

        # Check if target is wielding something that can parry,
        #    and if their Parry zone matches the Attacker's target zone.
        if target.weapon is not None and target.weapon.can_parry():
            parried = True

        if blocked or parried:
            # See if target can defend
            target_defense_stamina_cost = self.rules.get_defense_stamina_cost(
                attacker,
                AttackType.THROWN,
                stamina_cost,
                target
            )
            if target_defense_stamina_cost < target.stamina:
                target.spend_stamina(target_defense_stamina_cost)
                if range_to_target == CombatRange.MELEE:
                    attacker.cooldowns.add("attack", cooldown + 1)
                    target.add_buff("attack", 2, versus=attacker, duration=1)

                if blocked:
                    blocking_item = target.shield
                else:
                    blocking_item = target.weapon

                target.location.msg_contents(
                    "$You() $conj(block) the attack with $pron(your) {blocking_item}.",
                    mapping={"blocking_item": blocking_item},
                    from_obj=target,
                )
                return

        attack_roll = self.rules.roll(attacker, target, "cunning")
        target_size_penalty = 0
        if self.in_range(attacker, target, CombatRange.SHORT):
            range_penalty = 0
        else:
            # TODO Determine penalty
            range_penalty = 2

        defense_roll = 5 + target_size_penalty + range_penalty
        if attack_roll >= defense_roll:
            damage = random.randrange(min_damage, max_damage)
            damage += attacker.cunning

            # multiply the result by the Attackers Aggression factor (round up)
            if attacker.aggro == "defensive":
                damage = int(damage / 2)
            elif attacker.aggro == "aggressive":
                damage = int(damage * 1.5)

            # Subtract off the Target's armor, if any.
            if target.armor:
                damage = damage - target.armor
                if damage <= 0:
                    attacker.location.msg_contents(
                        "$pron(your) attack fails to pierce {target}'s {armor}.",
                        mapping={"target": target, "armor": target.armor},
                        from_obj=attacker,
                    )
                    return

            # apply the remainder to the Targets Health
            attacker.location.msg_contents(
                "$You() $conj(hit) {target} with $pron(your) thrown {weapon}.",
                mapping={"target": target, "weapon": weapon},
                from_obj=attacker,
            )
            target.at_damage(damage)

            return damage
        else:
            target.location.msg_contents(
                "$You() $conj(dodge) the attack.",
                from_obj=target,
            )
