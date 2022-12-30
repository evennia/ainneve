from random import randrange, randint
from .enums import CombatRange

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

    def get_range(self, attacker, target):
        """Get the distance from target in terms of weapon range."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        range = None
        for range_enum in CombatRange:
            range = range_enum.name
            if range_enum.value >= distance:
                break

        return range

    def in_range(self, attacker, target, range):
        """Check if target is within the specified range of attacker."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        range_enum = [en for en in CombatRange if en.name == range]
        if not range_enum:
            return False
        range_enum = range_enum[0]
        distance = abs(self.positions[attacker] - self.positions[target])
        return range_enum.value >= distance

    def any_in_range(self, attacker, range):
        if not (a_pos := self.positions.get(attacker)):
            return False

        range_enum = [en for en in CombatRange if en.name == range]
        if not range_enum:
            return False
        range_enum = range_enum[0]
        return any(
            p
            for c, p in self.positions.items()
            if abs(a_pos - p) <= range_enum.value and c != attacker
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
        roll += roller.attributes.get(stat)

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


    def at_attack(self, attacker, target, location="mm", attack_type="melee"):
        """
        Overall Attack function
        """
        blocked = False
        parried = False
        range_to_target = get_range(attacker, target)

        # assume the attack command parsing already checked that
        #      the attacker has no outstanding "adelay"

        # Make sure the attacker has a basic weapon, if not, default to "fist" melee weapon stats
        if attack_type == "melee" and attacker.weapon is None:
            weapon_type = "melee"
            min_damage = 1
            max_damage = 2
            stamina_cost = 2
            cooldown = 2

        # make sure the attacker has something to attack with during a ranged strike.
        elif (attack_type == "ranged" or attack_type == "thrown") and attacker.weapon is None:
            return -1

        # If this is a Throw attack, Determine "improvised" Damage
        elif attack_type == "thrown" and attacker.weapon.is_throwable is not None:
            # set the Base Physical Damage Range to 1-2 and the Base Stamina Cost to 4.
            weapon_type = "ranged"
            min_damage = 1
            max_damage = 2
            stamina_cost = 4
            cooldown = 4

        else:
            weapon_type = attack.weapon.weapon_type
            min_damage = attacker.weapon.min_damage
            max_damage = attacker.weapon.max_damage
            stamina_cost = attacker.weapon.stamina_cost
            cooldown = attacker.weapon.cooldown

        # Check to see if the attacker has enough Stamina for the attack
        #   based on weapon/spell, modified for their aggression and armor.
        attacker_stamina_cost = calc_attack_stamina_cost(attacker, attack_type, stamina_cost)
        if attacker_stamina_cost >= attacker.stamina:
            return -2

        # Subtract the Weapon/Armor/Aggression modified Stamina cost from the Attacker
        attacker.spend_stamina( attacker_stamina_cost )

        # Is the attack subject to block/parry defenses? (Can't block/parry spells)
        if attack_type in [ "melee", "thrown", "ranged" ]:
            # Check to see if the target is using a shield
            #   their Block zone matches the Attacker's target zone
            if target.shield is not None and calc_strikezone(location, target.block):
                blocked = True

            # Check if target is wielding something that can parry,
            #    and if their Parry zone matches the Attacker's target zone.
            if target.weapon is not None and target.weapon.can_parry() and calc_strikezone(location, target.parry):
                parried = True

            # See if target can defend (Note: Targets can Parry ranged attacks...)
            target_defense_stamina_cost = calc_defense_stamina_cost(target)
            if target_defense_stamina_cost < target.stamina and (blocked or parried):
                target.spend_stamina( target_defense_stamina_cost )
                if range_to_target == MELEE:
                    attacker.cooldowns.add("attack", cooldown+1)
                    target.add_buff("attack", 2, versus=attacker, duration=1)
                return -3 # successful defense, bail out early

        # Set the Attackers delay to the Weapon's delay time modified for Armor/Aggression
        attacker.cooldowns.add("attack", cooldown)

        if attack_type == "melee":
            attack_roll = roll(attacker, target, "strength")
            defense_roll = roll(target, attacker, "cunning", is_dodge=True)
        if attack_type == "ranged" or attack_type == "thrown":
            attack_roll = roll(attacker, target, "cunning")
            target_size_penalty = 0
            if is_range( attacker, target, "SHORT" ):
                range_penalty = 0
            defense_roll = 5 + target_size_penalty + range_penalty

        # did the conventional attack hit?
        if attack_type in [ "melee", "thrown", "ranged" ]:
            if attack_roll >= defense_roll:
                # generate a damage value from the Attackers weapon's base damage range
                damage = random.randrange(min_damage, max_damage)
                # Add Attackers Strength for Melee/Thrown attacks, Cunning for Ranged weapon attacks
                damage += ( attacker.strength if attack_type != "ranged" else attacker.cunning )
                # multiply the result by the Attackers Agression factor (round up)
                if attacker.aggro == "defensive":
                    damage = int(damage/2)
                elif attacker.aggro == "aggressive":
                    damage = int(damage*1.5)
                # Subtract off the Target's armor, if any.
                if target.armor != None:
                     damage = damage - target.armor
                if damage < 0:
                    return -4
                # apply the remainder to the Targets Health
                target.at_damage(damage)
                return damage
            else:
                return 0

        # Handle spell attacks
        if attack_type not in [ "melee", "thrown", "ranged" ]:
            attack_roll = roll(attacker, target, "will")
            defense_roll = 4 + target.will # TODO FIXME + target bonuses vrs spells
            if attack_roll >= defense_roll:
                # TODO FIXME effect = call spell's custom code by attack_type name
                effect = "Not implemented yet."
                return -5
            else:
                return -6
  
