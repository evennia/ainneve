"""
The Ainneve rulebook.

This module is an implementation of a simplified subset of the Open
Adventure rulebook. It contains a number of utility functions for
enforcing various game rules. See individual docstrings for more info.

Roll / Check Functions

    - `roll_max(xdyz)`
    - `d_roll(xdyz)`
    - `std_roll()`
    - `skill_check(skill, target=5)`

Rule System Functions

    - `resolve_combat`
    - `resolve_death`
    - `process_next_action`
    - `_do_*`

    This group of functions, along with the `CombatHandler` script class,
    comprises Ainneve's combat system. Each turn, the handler script will
    call `resolve_combat`, which performs an initiative roll for all players
    to determine turn order, and makes the first call to `process_next_action`.

    Using the determined turn order, `process_next_action` selects the appropriate
    `_do_*` function to carry out the next action, executes it, and sets a
    delayed call back to itself to handle the next action. After all actions
    are processed for a turn, control is returned to the `CombatHandler` to
    get input for the next turn.
"""

import re
import random
from math import floor
from collections import defaultdict
from evennia.utils import utils, make_iter


COMBAT_DELAY = 2
ACTIONS_PER_TURN = 2

COMBAT_DISTANCES = utils.variable_from_module('typeclasses.combat_handler', 'COMBAT_DISTANCES')
WRESTLING_POSITIONS = utils.variable_from_module('typeclasses.combat_handler', 'WRESTLING_POSITIONS')


class DiceRollError(Exception):
    """Default error class in die rolls/skill checks.

    Args:
        msg (str): a descriptive error message
    """
    def __init__(self, msg):
        self.msg = msg


def _parse_roll(xdyz):
    """Parser for XdY+Z dice roll notation.

    Args:
        xdyz (str): dice roll notation in the form of XdY[+|-Z][-DL]

            - _X_ - the number of dice to roll
            - _Y_ - the number of faces on each die
            - _+/-Z_ - modifier to add to the total after dice are rolled
            - _-DL_ - if the expression ends with literal L, sort the rolls
                and drop the lowest _D_ rolls before returning the total.
                _D_ can be omitted and will default to 1.

    """
    xdyz_re = re.compile(r'(\d+)d(\d+)([+-]\d+(?!L))?(?:-(\d*L))?')
    args = re.match(xdyz_re, xdyz)
    if not args:
        raise DiceRollError('Invalid die roll expression. Must be format `XdY[+-Z|-DL]`.')

    num, die, bonus, drop = args.groups()
    num, die = int(num), int(die)
    bonus = int(bonus or 0)
    drop = int(drop[:-1] or 1) if drop else 0

    if drop >= num:
        raise DiceRollError('Rolls to drop must be less than number of rolls.')

    return num, die, bonus, drop


def roll_max(xdyz):
    """Determines the maximum possible roll given an XdY+Z expression."""
    num, die, bonus, drop = _parse_roll(xdyz)
    return (num - drop) * die + bonus


def d_roll(xdyz, total=True):
    """Implementation of XdY+Z dice roll.

    Args:
        xdyz (str): dice roll expression in the form of XdY[+Z] or XdY[-Z]
        total (bool): if True, return a single value; if False, return a list
            of individual die values
    """
    num, die, bonus, drop = _parse_roll(xdyz)
    if bonus > 0 and not total:
        raise DiceRollError('Invalid arguments. `+-Z` not allowed when total is False.')

    rolls = [random.randint(1, die) for _ in range(num)]

    if drop:
        rolls = sorted(rolls, reverse=True)
        [rolls.pop() for _ in range(drop)]
    if total:
        return sum(rolls) + bonus
    else:
        return rolls


def std_roll():
    """An Open Adventure "Standard Roll" as described in the OA rulebook.

    Returns a number between -5 and +5, with 0 the most common result.
    """
    white, black = d_roll('2d6', total=False)
    if white >= black:
        return white - black
    else:
        return -(black - white)


def skill_check(skill, target=5):
    """A basic Open Adventure Skill check.

    This is used for skill checks, trait checks, save rolls, etc.

    Args:
        skill (int): the value of the skill to check
        target (int): the target number for the check to succeed

    Returns:
        (bool): indicates whether the check passed or failed
    """
    return skill + std_roll() >= target


def resolve_death(killer, victim, combat_handler):
    """Called when a victim is killed during combat.

    Args:
        killer (Character): the character causing `victim`'s death
        victim (Character): the character being killed
        combat_handler (CombatHandler): combat in which the killing is happening
    """
    killer.location.msg_contents(
        "{killer} has vanquished {victim}.",
        mapping={'killer': killer, 'victim': victim},
        exclude=victim)

    victim.at_death()
    combat_handler.remove_character(victim)
    combat_handler.db.turn_order.remove(victim.id)

    # award XP
    if victim.is_typeclass('typeclasses.characters.Character'):
        # in PVP, gain 10% of opponents XP
        xp_gained = int(floor(0.1 * victim.traits.XP.actual))
    else:
        # XP trait on NPCs contains the full award
        xp_gained = int(victim.traits.XP.actual)

    killer.traits.XP.base += xp_gained
    killer.msg("{actor} gains {xp} XP".format(
        actor=killer.get_display_name(killer),
        xp=xp_gained))


def _do_nothing(st_remaining, character, _, args):
    """Default combat action if no action has been entered."""
    if st_remaining <= 0:  # only message on the last repeat
        ch = character.ndb.combat_handler
        ch.combat_msg(
            "{actor} stares into space vacantly.",
            actor=character)

        return 0.5 * COMBAT_DELAY
    else:
        return 0.2 * COMBAT_DELAY


def _do_drop(st_remaining, character, target, _):
    """Implement the 'drop item' combat action."""
    ch = character.ndb.combat_handler
    # drop the item and run hook
    if target in character.contents:
        if target in character.equip:
            character.equip.remove(target)
            if hasattr(target, 'at_remove'):
                target.at_remove(character)

        target.move_to(character.location, quiet=True)
        if hasattr(target, 'at_drop'):
            target.at_drop(character)

        # messaging
        ch.combat_msg(
            "{actor} drops {item}.",
            actor=character,
            item=target)

        return 0.5 * COMBAT_DELAY

    else:
        ch.combat_msg(
            "{actor} searches their bag, looking for {item}.",
            actor=character,
            item=target)

        return 0.2 * COMBAT_DELAY


def _do_get(st_remaining, character, target, _):
    """Implement the 'get item' combat action."""
    ch = character.ndb.combat_handler
    if target in character.location.contents:
        # get the item and run hook
        target.move_to(character, quiet=True)
        if hasattr(target, 'at_get'):
            target.at_get(character)

        # messaging
        ch.combat_msg(
            "{actor} gets {item}.",
            actor=character,
            item=target)

        return 1 * COMBAT_DELAY

    else:
        ch.combat_msg(
            "{actor} searches around looking for {target}.",
            actor=character,
            target=target)

        return 0.5 * COMBAT_DELAY


def _do_equip(st_remaining, character, target, _):
    """Implement the 'equip' combat action, replacing any
    currently equipped item.
    """
    ch = character.ndb.combat_handler
    # confirm the item is in character's possesion
    if target not in character.contents:
        ch.combat_msg(
            "{actor} looks around, confused.",
            actor=character,
            item=target)
        return 0 * COMBAT_DELAY

    # handle swapping items if needed
    occupied_slots = [character.equip.get(s) for s in target.db.slots
                      if character.equip.get(s)]
    if occupied_slots:
        for item in occupied_slots:
            character.equip.remove(item)
            ch.combat_msg(
                "{actor} removes {item}.",
                actor=character,
                item=item)

    # equip the item and call hooks
    if not character.equip.add(target):
        ch.combat_msg(
            "{actor} looks at {item}, wasting precious time.",
            actor=character,
            item=target)

        return 0 * COMBAT_DELAY

    if hasattr(target, "at_equip"):
        target.at_equip(character)

    # messaging
    ch.combat_msg(
        "{actor} equips {item}.",
        actor=character,
        item=target)

    return 1 * COMBAT_DELAY


def _do_remove(st_remaining, character, target, _):
    """Implement the 'remove' combat action, removing a
    currently equipped item.
    """
    ch = character.ndb.combat_handler
    # confirm the item is in character's possesion
    if target not in character.equip:
        ch.combat_msg(
            "{actor} looks around, confused.",
            actor=character,
            item=target)
        return 0 * COMBAT_DELAY

    # remove the item and call hooks
    if not character.equip.remove(target):
        ch.combat_msg(
            "{actor} adjusts {item}, wasting precious time.",
            actor=character,
            item=target)

        return 0 * COMBAT_DELAY

    if hasattr(target, "at_remove"):
        target.at_remove(character)

    # messaging
    ch.combat_msg(
        "{actor} removes {item}.",
        actor=character,
        item=target)

    return 1 * COMBAT_DELAY


def _do_attack(st_remaining, character, target, args):
    """Implement melee and ranged 'attack' ch actions."""
    ch = character.ndb.combat_handler

    # confirm the target is still in combat
    if not target.id in ch.db.characters:
        ch.combat_msg(
            "{actor} is unable to attack {defender}.",
            actor=character,
            defender=target)

        return 0.2 * COMBAT_DELAY

    if character.db.position != 'STANDING':
        # if you are in any wrestling position other
        # than free standing, all you can do is wrestle to break free
        return _do_wrestle(character, target, ['break'])

    attack_range = ch.get_range(character, target)

    # determine whether there is an equipped weapon for that range
    weapons = set([character.equip.get(s) for s in character.equip.slots
                   if s.startswith('wield')
                   and character.equip.get(s) is not None])

    weapon_ranges = dict(melee=('melee',),
                         reach=('reach', 'melee'),
                         ranged=('ranged', 'reach'))
    weapon = None
    for weap in weapons:
        if weap.attributes.has('range'):
            if attack_range in weapon_ranges[weap.db.range]:
                weapon = weap

    if not weapon:
        ch.combat_msg(
            "{actor} does not have a weapon that can attack opponents at |G{range}|n distance.",
            actor=character,
            range=attack_range)
        return 0

    # check whether the target is dodging
    dodging = target.nattributes.has('dodging')

    if dodging:
        # attacker must take the worse of two standard rolls
        atk_roll = min((std_roll(), std_roll()))
    else:
        atk_roll = std_roll()

    ammunition = None
    if weapon.db.range in ('melee', 'reach'):
        # calculate damage
        damage = (atk_roll + character.traits.ATKM) - target.traits.DEF

    else:  # weapon range is 'ranged'
        # confirm we have proper ammunition
        ammunition = weapon.get_ammunition_to_fire()

        if not ammunition:
            ch.combat_msg(
                "{actor} does not have any {ammo}s in their quiver.",
                actor=character,
                ammo=weapon.db.ammunition)
            return 0

        if attack_range == 'reach':
            # ranged weapons get a +1 bonus at reach range
            character.traits.ATKR.mod += 1

        # calculate damage
        damage = (atk_roll + character.traits.ATKR) - target.traits.DEF

        if attack_range == 'reach':
            # remove the bonus
            character.traits.ATKR.mod -= 1

    # apply damage
    if damage > 0:
        if ammunition:
            # ammunition goes into target
            ammunition.move_to(target, quiet=True)

        if dodging:
            ch.combat_msg(
                "{actor} tries to dodge, but",
                actor=target)

        if any((arg.startswith('s') for arg in args)):
            # 'subdue': deduct stamina instead of health
            if target.traits.SP >= damage:
                target.traits.SP.current -= damage
                status = 'dmg_sp'
            else:
                # if we don't have enough SP, damages HP instead
                damage = damage - target.traits.SP
                target.traits.SP.current = 0
                target.traits.HP.current -= damage
                status = 'dmg_hp'

        else:
            target.traits.HP.current -= damage
            status = 'dmg_hp'
    else:
        if ammunition:
            # ammunition falls to the ground
            ammunition.move_to(target.location, quiet=True)

        if dodging:
            status = 'dodged'
        else:
            status = 'missed'

    ch.combat_msg(
        weapon.db.messages[status],
        actor=character,
        target=target,
        weapon=weapon)

    # handle Power Points
    if atk_roll > 0:
        # this attack has earned PPs
        character.traits.PP.current += atk_roll

    if character.traits.PP.actual > 0:
        # handle equipment abilities
        pass

    if target.traits.HP.actual <= 0:
        # target has died
        resolve_death(character, target, ch)

    return 1 * COMBAT_DELAY


def _do_kick(st_remaining, character, target, args):
    """Implements the 'kick' combat command."""
    ch = character.ndb.combat_handler

    # if character.db.position != 'STANDING':
    #     # if you are in any wrestling position other
    #     # than free standing, all you can do is wrestle to break free
    #     return _do_wrestle(character, target, ['break'])

    # kicking takes two-subturns to complete
    if st_remaining > 0:
        # irst subturn: messaging only
        ch.combat_msg(
            "{actor} takes a step toward {target}.",
            actor=character,
            target=target)

    else:
        # second subturn: checks and resolution

        # confirm the target is still in combat and is within range
        attack_range = ch.get_range(character, target)
        if target.id not in ch.db.characters \
                or attack_range != 'melee':
            ch.combat_msg(
                "{actor} is unable to kick {target}.",
                actor=character,
                target=target)

            return 0.2 * COMBAT_DELAY

        # check whether the target is dodging
        dodging = target.nattributes.has('dodging')

        if dodging:
            # attacker must take the worse of two standard rolls
            atk_roll = min((std_roll(), std_roll()))
        else:
            atk_roll = std_roll()

        damage = (atk_roll + character.traits.ATKU + 2) - target.traits.DEF
        if damage > 0:
            if dodging:
                ch.combat_msg(
                    "{actor} tries to dodge, but",
                    actor=target
                )

            if any((arg.startswith('s') for arg in args)):
                # 'subdue': deduct stamina instead of health
                if target.traits.SP >= damage:
                    target.traits.SP.current -= damage
                    status = 'dmg_sp'
                else:
                    # if we don't have enough SP, damages HP instead
                    damage = damage - target.traits.SP
                    target.traits.SP.current = 0
                    target.traits.HP.current -= damage
                    status = 'dmg_hp'

            else:
                target.traits.HP.current -= damage
                status = 'dmg_hp'

        else:
            if dodging:
                status = 'dodged'
            else:
                status = 'missed'

            # TODO: add 'off-balance' status effect to character once effects are implemented

        messages = {
            'dmg_hp': "{actor} kicks {target} savagely, sending them reeling.",
            'dmg_sp': "{actor} kicks {target} squarely in the chest, and {target} "
                       "staggers from the blow.",
            'dodged': "{target} dodges a kick from {actor}, throwing {actor} off balance.",
            'missed': "{actor} kicks toward {target} and misses."
        }

        ch.combat_msg(
            messages[status],
            actor=character,
            target=target)

        # handle Power Points
        if atk_roll > 0:
            # this attack has earned PPs
            character.traits.PP.current += atk_roll

        if character.traits.PP.actual > 0:
            # handle equipment abilities
            pass

        if target.traits.HP.actual <= 0:
            # target has died
            resolve_death(character, target, ch)

    return 1 * COMBAT_DELAY


def _do_strike(st_remaining, character, target, args):
    """Implements the 'strike' combat command."""
    ch = character.ndb.combat_handler

    if character.db.position != 'STANDING' and 'end' not in args:
        # if you are in any wrestling position other
        # than free standing, all you can do is wrestle to break free
        return _do_wrestle(character, target, ['break'])

    # confirm the target is still in combat,
    if target.id not in ch.db.characters:
        character.msg("{defender} has left combat.".format(
            defender=target.get_display_name(character)))
        return 0.2 * COMBAT_DELAY

    # is within range,
    attack_range = ch.get_range(character, target)
    if attack_range != 'melee':
        ch.combat_msg(
            "{actor} is too far away from {target} to strike them.",
            actor=character,
            target=target)
        return 0.2 * COMBAT_DELAY

    # and has at least one free hand
    strikes = sum(1 if character.equip.get(slot) is None else 0
                  for slot in character.db.slots
                  if slot.startswith('wield'))

    if strikes <= 0:
        ch.combat_msg(
            "{actor} goes to punch, but does not have a free hand.",
            actor=character)
        return 0.2 * COMBAT_DELAY

    # check whether the target is dodging
    dodging = target.nattributes.has('dodging')

    if dodging:
        # attacker must take the worse of two standard rolls
        atk_roll = min((std_roll(), std_roll()))
    else:
        atk_roll = std_roll()

    damage = (atk_roll + character.traits.ATKU) - target.traits.DEF
    if damage > 0:
        if dodging:
            ch.combat_msg(
                "{actor} tries to dodge, but",
                actor=target
            )

        if any((arg.startswith('s') for arg in args)):
            # 'subdue': deduct stamina instead of health
            if target.traits.SP >= damage:
                target.traits.SP.current -= damage
                status = 'dmg_sp'
            else:
                # if we don't have enough SP, damages HP instead
                damage = damage - target.traits.SP
                target.traits.SP.current = 0
                target.traits.HP.current -= damage
                status = 'dmg_hp'

        else:
            target.traits.HP.current -= damage
            status = 'dmg_hp'
    else:
        if dodging:
            status = 'dodged'
        else:
            status = 'missed'

    messages = {
        'dmg_hp': "{actor} strikes {target} savagely with their fist.",
        'dmg_sp': "{actor} strikes {target} hard in the chest, and {target} "
                   "staggers from the blow.",
        'dodged': "{target} dodges a punch from {actor}.",
        'missed': "{actor} attempts to punch {target} and misses."
    }

    ch.combat_msg(
        messages[status],
        actor=character,
        target=target)

    # handle Power Points
    if atk_roll > 0:
        # this attack has earned PPs
        character.traits.PP.current += atk_roll

    if character.traits.PP.actual > 0:
        # handle equipment abilities
        pass

    if target.traits.HP.actual <= 0:
        # target has died
        resolve_death(character, target, ch)

    if 'end' not in args:
        if strikes > 1:
            # we have two free hands; do a second strike
            args.append('end')
            utils.delay(0.5 * COMBAT_DELAY, _do_strike, 0, character, target, args)

        return 1 * COMBAT_DELAY


def _do_advance(st_remaining, character, target, args):
    """Implements the 'advance' combat command."""
    ch = character.ndb.combat_handler
    start_range = ch.get_range(character, target)
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'melee'

    if start_range == end_range:
        ch.combat_msg(
            "{actor} is already at |G{range}|n with {target}.",
            actor=character,
            range=end_range,
            target=target
        )
        return 0.2 * COMBAT_DELAY

    elif start_range == 'melee':
        ch.combat_msg(
            "{actor} cannot advance any farther on {target}.",
            actor=character,
            target=target
        )
        return 0.2 * COMBAT_DELAY

    ch.move_character(character, end_range, target)

    ch.combat_msg(
        "{actor} advances to |G{range}|n range with {target}.",
        actor=character,
        target=target,
        range=end_range)

    return 1 * COMBAT_DELAY


def _do_retreat(st_remaining, character, _, args):
    """Implements the 'retreat' combat command."""
    ch = character.ndb.combat_handler
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'ranged'
    start_range = ch.get_min_range(character)

    if start_range == end_range:
        ch.combat_msg(
            "{actor} has already retreated to |G{range}|n range.",
            actor=character,
            range=end_range)

        return 0.2 * COMBAT_DELAY

    elif start_range == 'melee':
        ok = skill_check(character.skills.balance.actual, 4)

    else:
        ok = True

    if ok:
        ch.move_character(character, end_range)
        ch.combat_msg(
            "{actor} retreats to |G{range}|n distance.",
            actor=character,
            range=end_range)
    else:
        ch.combat_msg(
            "{actor} attempts to retreat but stumbles and is unable.",
            actor=character)

    return 1 * COMBAT_DELAY


def _do_dodge(*args):
    """Dodging is handled in attack actions.
       This is just a placeholder."""
    return 0


def _do_flee(st_remaining, character, _, args):
    """Implements the 'flee' combat command."""
    ch = character.ndb.combat_handler
    # fleeing takes two subturns
    if st_remaining > 0:
        # first subturn: messaging only
        ch.combat_msg(
            "{actor} looks about frantically for an escape route.",
            actor=character)
    else:
        # second subturn: skill check and resolution
        min_range = ch.get_min_range(character)

        if min_range == 'melee':
            # very difficult
            target_num = 9
        elif min_range == 'reach':
            # moderately difficult
            target_num = 6
        else:  # min_range == 'ranged'
            # easiest
            target_num = 4

        ok = skill_check(character.skills.escape.actual, target_num)
        if ok:
            # successfully escaped
            ch.combat_msg(
                "{actor} seizes the opportunity to escape the fight!",
                actor=character)
            ch.remove_character(character)

            character.msg("{actor} knows they are safe, for a time...".format(
                actor=character.get_display_name(character)))

            # prevent re-attack for a time
            character.ndb.no_attack = True
            safe_time = 2 * (character.skills.escape + d_roll('1d6'))

            def enable_attack():
                del character.ndb.no_attack
                character.msg("{actor} feels somehow more vulnerable than just a moment ago.".format(
                    actor=character.get_display_name(character)))

            utils.delay(safe_time, enable_attack)
        else:
            # failed to escape
            ch.combat_msg(
                "{actor} tries to escape, but is boxed in.",
                actor=character)

    return 1 * COMBAT_DELAY


def _do_wrestle(st_remaining, character, target, args):
    """Implements the 'wrestle' combat command."""
    return 0 * COMBAT_DELAY


def process_next_action(combat_handler):
    """
    Callback that handles processing combat actions

    Args:
        combat_handler: instance of a combat handler

    Returns:
        None

    Based on the combat handler's data, this callback
    selects an appropriate `_do_*` function to execute
    the combat action. These handlers are all called
    with the signature:

        `_do_action(subturns_remaining, character, target, args)`

    Each `_do_*` function should return a time delay
    in seconds before the next call to `process_next_action`
    should be run.
    """
    turn_actions = combat_handler.db.turn_actions
    turn_order = combat_handler.db.turn_order
    actor_idx = combat_handler.db.actor_idx
    delay = 0

    if actor_idx >= len(turn_order):
        # finished a subturn
        # reset counters and see who is dodging during the next action
        combat_handler.ndb.actions_taken = defaultdict(int)
        combat_handler.db.actor_idx = actor_idx = 0
        for dbref, char in combat_handler.db.characters.items():
            if char.nattributes.has('dodging'):
                del char.ndb.dodging
            action_count = 0

            # set the dodging nattribute on any characters
            # with 'dodge' as their action
            for action, _, _, duration in combat_handler.db.turn_actions[dbref]:
                if action == 'dodge':
                    char.ndb.dodging = True
                    break
                action_count += duration
                if action_count >= 1:
                    break

        # and increment the subturn
        combat_handler.db.subturn += 1

    if combat_handler.db.subturn > ACTIONS_PER_TURN:
        # turn is over; notify the handler to start the next
        combat_handler.begin_turn()
        return

    current_charid = turn_order[actor_idx]
    if combat_handler.ndb.actions_taken[current_charid] < 1:
        action, character, target, duration = \
            turn_actions[current_charid].popleft()

        combat_handler.ndb.actions_taken[current_charid] += duration

        args = action.split('/')[1:]

        # we decrement the duration for this turn
        duration -= 1
        if duration > 0:
            # action takes more than one subturn; return it to the queue
            turn_actions[current_charid].append(
                (action,
                 character,
                 target,
                 duration)
            )
            combat_handler.db.actor_idx += 1

        action_func = '_do_{}'.format(action.split('/')[0])

        # action_func receives the number of subturns remaining in the action
        delay = globals()[action_func](duration, character, target, args)
    else:
        combat_handler.db.actor_idx += 1

    if len(combat_handler.db.characters) < 2:
        combat_handler.stop()
    else:
        utils.delay(delay, process_next_action, combat_handler)


def resolve_combat(combat_handler):
    """Called by the combat handler to resolve combat.

    Each turn, an initiative roll is done behind the scenes
    for all combat participants. This determines the order
    that the `process_next_action` function executes the actions.

    According to OA combat rules, each turn is handled as two
    subturns. It is possible to modify the number of subturns
    in each turn by modifying the `ACTIONS_PER_TURN` module
    variable above.

    Args:
        combat_handler: an instance of the combat handler
                invoking this function
    """
    combatants = combat_handler.db.characters

    # fill any dawdlers with the 'nothing' action
    for dbref in combat_handler.db.action_count.keys():
        if combat_handler.db.action_count[dbref] < ACTIONS_PER_TURN:
            combat_handler.add_action(
                'nothing',
                combat_handler.db.characters[dbref],
                None,
                ACTIONS_PER_TURN - combat_handler.db.action_count[dbref])

    # tiebreaker resolution helper function. super non-deterministic
    def _initiative_cmp(x, y):
        # first tiebreaker: result of the std_roll
        if x[2] != y[2]:
            return y[2] - x[2]
        else:
            # second tiebreaker: PCs before NPCs
            x_plyr, y_plyr = combatants[x[0]].has_account, \
                             combatants[y[0]].has_account
            if x_plyr and not y_plyr:
                return 1
            elif y_plyr and not x_plyr:
                return -1
            else:
                # third tiebreaker: reroll
                while True:  # repeat until we get a result
                    roll_x = std_roll() + combatants[x[0]].traits.PER.actual
                    roll_y = std_roll() + combatants[y[0]].traits.PER.actual
                    if roll_x != roll_y:
                        return roll_x - roll_y

    # Do the Initiative roll to determine turn order
    turn_order = []
    intv_rolls = {}

    for cid, combatant in combatants.items():
        roll = std_roll()
        initiative = roll + combatant.traits.PER.actual
        if initiative in intv_rolls:
            intv_rolls[initiative].append((cid, initiative, roll))
        else:
            intv_rolls[initiative] = [(cid, initiative, roll)]

    # resolve ties and build the turn order
    for intv in sorted(intv_rolls.keys(), reverse=True):
        if len(intv_rolls[intv]) == 1:
            turn_order += [intv_rolls[intv][0][0]]
        else:  # more than one rolled same Initiative
            turn_order += [x[0] for x in
                           sorted(intv_rolls[intv], cmp=_initiative_cmp)]

    combat_handler.db.turn_order = turn_order
    combat_handler.db.subturn = 0

    # here, actor_idx is initialized to trigger the "end"
    # of subturn 0 within the process_next_action call
    combat_handler.db.actor_idx = len(turn_order)

    # begin processing actions for characters in order
    process_next_action(combat_handler)

