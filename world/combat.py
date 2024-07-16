import random
from random import randrange
from typing import Self

from .enums import CombatRange, AttackType

_MAX_RANGE = max([en.value for en in CombatRange])

# format for combat prompt, currently unused
# health, mana, current attack cooldown
COMBAT_PROMPT = "HP {hp} - MP {mana} - SP {stamina}"


class CombatHandler:
    positions = None

    def __init__(self, attacker, target):
        # the starting position logic could be better
        self.positions = {attacker: 1, target: 2}
        attacker.ndb.combat = self
        target.ndb.combat = self

    @classmethod
    def get_or_create(cls, attacker, target) -> Self:
        attacker_combat: Self = attacker.ndb.combat
        target_combat: Self = target.ndb.combat

        if attacker_combat and target_combat:
            # both parties are in separate combat instances; combine into one
            attacker_combat.merge(target.ndb.combat)
            return attacker_combat
        elif attacker_combat:
            attacker_combat.add(target)
            return attacker_combat
        elif target_combat:
            target_combat.add(attacker)
            return target_combat
        else:
            # neither are in combat; start new instance
            combat = CombatHandler(attacker, target)
            return combat

    def add(self, participant):
        """Add a new combatant to the combat instance."""
        # only add if they aren't already part of the fight
        if participant not in self.positions:
            self.positions[participant] = 0
            participant.ndb.combat = self

    def remove(self, participant):
        """Removes a combatant from the combat instance."""
        # only remove if they're actually in combat
        if participant in self.positions:
            self.positions.pop(participant)
            participant.nattributes.remove("combat")

            survivors = list(self.positions.keys())
            if len(survivors) == 1:
                # only one participant means no more fight
                survivors[0].nattributes.remove("combat")
                self.positions = None

    def merge(self, other):
        """Merge another combat instance into this one"""
        # an entity can't be in two combat instances at once, so there should be no dupes
        self.positions |= other.positions
        for obj in other.positions.keys():
            obj.ndb.combat = self
        other.positions = None

    def get_range(self, attacker, target) -> CombatRange:
        """Get the distance from target in terms of weapon range."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        for range_enum in CombatRange:
            if range_enum.value >= distance:
                return range_enum

        return CombatRange.RANGED

    def in_range(self, attacker, target, combat_range: CombatRange):
        """Check if target is within the specified range of attacker."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        return distance <= combat_range

    def any_in_range(self, attacker, combat_range: CombatRange):
        if not (a_pos := self.positions.get(attacker)):
            return False

        return any(
            p
            for c, p in self.positions.items()
            if abs(a_pos - p) <= combat_range and c != attacker
        )

    def approach(self, mover, target):
        """
        Move a combatant towards the target.
        Returns True if the distance changed, or False if it didn't.
        """
        # both combatants must be in combat
        if not (mover in self.positions and target in self.positions):
            return False

        start = self.positions[mover]
        end = self.positions[target]

        if start == end:
            # already as close as you can get
            return False

        change = 1 if start < end else -1
        self.positions[mover] += change
        return True

    def retreat(self, mover, target):
        """
        Move a combatant away from the target.
        Returns True if the distance changed, or False if it didn't.
        """
        # both combatants must be in combat
        if not (mover in self.positions and target in self.positions):
            return False

        start = self.positions[mover]
        end = self.positions[target]

        # can't move beyond maximum weapon range
        if abs(start - end) >= _MAX_RANGE:
            return False

        change = -1 if start < end else 1
        self.positions[mover] += change
        return True

    def roll(self, roller, target, stat, is_dodge=False):
        """
        Roll 2d6 + roller's stat +/- roller's aggression + applicable bonuses
        """
        roll = randrange(1,6) + randrange(1,6)
        roll += roller.attributes.get(stat, 0)

        if is_dodge:
            if roller.aggro == "aggressive":
                roll += -1
            elif roller.aggro == "defensive":
                roll += 1
        else:
            if roller.aggro == "aggressive":
                roll += 1
            elif roller.aggro == "defensive":
                roll += -1

        # TODO FIXME Add any bonuses this roller has versus the given target
        roll += 0

        return roll

    def calc_strikezone(self, attack_location, defense_location):
        """
        We can expand on this to include adjacent sides/etc or weightings/corners
        """
        return (attack_location == defense_location)

    def calc_attack_stamina_cost(self, attacker, attack_type, base_cost):
        if attacker.aggro == "aggressive":
            cost = int(base_cost * 1.5)
        elif attacker.aggro == "defensive":
            cost = int(base_cost/2)
        else:
            cost = base_cost
        return cost

    def calc_defense_stamina_cost(self, target):
        return 2   # TODO FIXME update this

    def at_melee_attack(self, attacker, target):
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

        attacker_stamina_cost = self.calc_attack_stamina_cost(attacker, AttackType.MELEE, stamina_cost)
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
            target_defense_stamina_cost = self.calc_defense_stamina_cost(target)
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

        attack_roll = self.roll(attacker, target, "strength")
        defense_roll = self.roll(target, attacker, "cunning", is_dodge=True)
        if attack_roll >= defense_roll:
            damage = random.randrange(min_damage, max_damage)
            damage += attacker.strength

            # multiply the result by the Attackers Agression factor (round up)
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

        attacker_stamina_cost = self.calc_attack_stamina_cost(attacker, AttackType.RANGED, stamina_cost)
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
            target_defense_stamina_cost = self.calc_defense_stamina_cost(target)
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

        attack_roll = self.roll(attacker, target, "cunning")
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

            # multiply the result by the Attackers Agression factor (round up)
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

        attacker_stamina_cost = self.calc_attack_stamina_cost(attacker, AttackType.THROWN, stamina_cost)
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
            target_defense_stamina_cost = self.calc_defense_stamina_cost(target)
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

        attack_roll = self.roll(attacker, target, "cunning")
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

            # multiply the result by the Attackers Agression factor (round up)
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
