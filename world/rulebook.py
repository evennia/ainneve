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

"""

import re
import random
from math import floor
from collections import defaultdict
from evennia.utils import utils, make_iter


COMBAT_DELAY = 1
ACTIONS_PER_TURN = 2

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
    """Called when a victim is killed during combat."""
    victim.at_death()
    combat_handler.remove_character(victim)
    combat_handler.db.turn_order.remove(victim.id)

    killer.msg("You have defeated {target}.".format(
        target=victim.get_display_name(killer)
    ))
    killer.location.msg_contents(
        "{character} has vanquished {target}.",
        mapping=dict(character=killer,
                     target=victim),
        exclude=(killer, victim)
    )
    # award XP
    xp_gained = int(floor(0.1 * victim.traits.XP.actual))
    killer.traits.XP.base += xp_gained
    killer.msg("You gain {} XP".format(xp_gained))


def _do_nothing(character, *args):
    character.msg("Your attention wanders, despite the heated battle raging around you.")
    character.location.msg_contents(
        "{char} stares into space vacantly.",
        mapping=dict(char=character),
        exclude=character)
    return 0.5 * COMBAT_DELAY


def _do_drop(character, target, _):
    """Implement the 'drop item' combat action."""
    target.move_to(character.location, quiet=True)
    character.msg("You drop {}.".format(target.get_display_name(character)))
    character.location.msg_contents(
        "{char} drops {obj}.",
        mapping=dict(char=character,
                     obj=target),
        exclude=character)
    # Call the object script's at_drop() method.
    target.at_drop(character)
    return 0.2 * COMBAT_DELAY


def _do_get(character, target, _):
    """Implement the 'get item' combat action."""
    return 0 * COMBAT_DELAY


def _do_equip(character, *args):
    """Implement the 'equip' combat action, replacing any
    currently equipped item.
    """
    return 0 * COMBAT_DELAY


def _do_attack(character, target, args):
    """Implement melee and ranged 'attack' combat actions."""

    # first, determine combat range
    combat_handler = character.ndb.combat_handler

    # confirm the target is still in combat
    if not target.id in combat_handler.db.characters:
        character.msg("You are unable attack {target}.".format(
            target=target.get_display_name(character)
        ))
        character.location.msg_contents(
            "{character} is unable to attack {target}.",
            mapping=dict(character=character,
                         target=target),
            exclude=(character, target)
        )
        return 0.2 * COMBAT_DELAY

    if character.db.position != 'STANDING':
        character.msg("You cannot attack while wrestling.")
        return 0.2 * COMBAT_DELAY

    attack_range = combat_handler.get_range(character, target)

    # determine whether there is an equipped weapon for that range
    weapons = set([character.equip.get(s) for s in character.equip.slots
                   if s.startswith('wield')
                   and character.equip.get(s) is not None])

    weapons_by_range = defaultdict(list)
    for weapon in weapons:
        if weapon.attributes.has('range'):
            for rng in make_iter(weapon.db.range):
                weapons_by_range[rng].append(weapon)

    attack_type = None

    if attack_range == 'melee' and weapons_by_range['melee']:
        attack_type = 'melee'

    elif attack_range == 'reach':
        if weapons_by_range['reach']:
            attack_type = 'reach'

        elif weapons_by_range['ranged']:
            attack_type = 'ranged'
            character.traits.ATKR.mod += 1

    else:  # attack_range == COMBAT_DISTANCES['ranged']
        if weapons_by_range['ranged']:
            attack_type = 'ranged'

    if not attack_type:
        character.msg("You do not have an appropriate weapon to attack.")
        return 0

    weapon = weapons_by_range[attack_type][0]

    # check whether the target is dodging
    dodging = target.nattributes.has('dodging')

    if dodging:
        # attacker must take the worse of two standard rolls
        atk_roll = min((std_roll(), std_roll()))
    else:
        atk_roll = std_roll()

    ammunition = None
    if attack_type == 'melee':
        # calculate damage
        damage = (atk_roll + character.traits.ATKM.actual) - \
            target.traits.DEF.actual

    else:  # attack_type == 'ranged'
        # confirm we have proper ammunition
        ammunition = weapon.get_ammunition_to_fire()

        if not ammunition:
            character.msg("You do not have any {}s".format(
                weapon.db.ammunition))
            return 0

        # calculate damage
        damage = (atk_roll + character.traits.ATKR.actual) - \
            target.traits.DEF.actual

    # apply damage
    if damage > 0:
        if ammunition:
            # ammunition goes into target
            ammunition.move_to(target, quiet=True)

        if dodging:
            target.msg("You try to dodge the incoming attack, but")
            character.location.msg_contents(
                "{target} tries to dodge, but",
                mapping=dict(target=target),
                exclude=target
            )

        if any((arg.startswith('s') for arg in args)):
            # 'subdue': deduct stamina instead of health
            target.traits.SP.current -= damage
            character.msg(
                ("You stun {target} with {weapon}, "
                 "closer to submission.").format(
                    target=target.get_display_name(character),
                    weapon=weapon.get_display_name(character)
                )
            )
            target.msg(
                ("{character} stuns you with "
                 "{weapon}, sapping your strength.").format(
                    character=character.get_display_name(target),
                    weapon=weapon.get_display_name(target)
                )
            )
            character.location.msg_contents(
                "{character} stuns {target} with {weapon}." ,
                mapping=dict(character=character,
                             target=target,
                             weapon=weapon),
                exclude=(character, target)
            )
        else:
            target.traits.HP.current -= damage
            character.msg(
                ("You attack {target} with {weapon}, "
                 "hurting them so bad.").format(
                    target=target.get_display_name(character),
                    weapon=weapon.get_display_name(character)
                )
            )
            target.msg(
                "{character} attacks you with {weapon}.".format(
                    character=character.get_display_name(target),
                    weapon=weapon.get_display_name(target)
                )
            )
            character.location.msg_contents(
                "{character} attacks {target} with {weapon}.",
                mapping=dict(character=character,
                             target=target,
                             weapon=weapon),
                exclude=(character, target)
            )
    else:
        if ammunition:
            # ammunition falls to the ground
            ammunition.move_to(target.location, quiet=True)

        if dodging:
            character.msg(
                ("{target} dodges your attack, and |/"
                 "{weapon} falls through the air impotently").format(
                    target=target.get_display_name(character),
                    weapon=weapon.get_display_name(character)
                 )
            )
            target.msg(
                "You successfully dodge {character}'s attack.".format(
                    character=character.get_display_name(target)
                )
            )
            character.location.msg_contents(
                ("{weapon} fails to meet its target as {target}"
                 "dodges {character}'s attack."),
                mapping=dict(weapon=weapon,
                             target=target,
                             character=character),
                exclude=(character, target)
            )
        else:
            character.msg(
                "You attack {target} with {weapon} and miss.".format(
                    weapon=weapon.get_display_name(character),
                    target=target.get_display_name(character)
                )
            )
            target.msg(
                "{character} attacks you with {weapon} and misses.".format(
                    character=character.get_display_name(target),
                    weapon=weapon.get_display_name(target)
                )
            )
            character.location.msg_contents(
                "{character} attacks {target} with {weapon} and misses.",
                mapping=dict(character=character,
                             weapon=weapon,
                             target=target),
                exclude=(character, weapon)
            )

    # handle Power Points
    if atk_roll > 0:
        # this attack has earned PPs
        character.traits.PP.current += atk_roll

    if character.traits.PP.actual > 0:
        # handle equipment abilities
        pass

    if target.traits.HP.actual <= 0:
        # target has died
        resolve_death(character, target, combat_handler)

    if attack_range == 'reach' and attack_type == 'ranged':
        # remove the range bonus
        character.traits.ATKR.mod -= 1

    return 1 * COMBAT_DELAY


def _do_advance(character, target, args):
    """Implements the 'advance' combat command."""
    combat_handler = character.ndb.combat_handler
    start_range = combat_handler.get_range(character, target)
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'melee'

    if start_range == end_range:
        character.msg("You are already at {range} with {target}.".format(
            range=end_range,
            target=target.get_display_name(character)
        ))
        return 0.2 * COMBAT_DELAY

    ok = combat_handler.move_character(character, end_range, start_range, target)

    if ok:
        character.msg("You advance on {target} to {range} range.".format(
            target=target.get_display_name(character),
            range=end_range
        ))
        target.msg("{character} advances on you to {range} range.".format(
            character=character.get_display_name(target),
            range=end_range
        ))
        # used double braces here because this string gets run
        # through format() twice, once here to substitute 'range'
        # and again in msg_contents for each room occupant
        character.location.msg_contents(
            "{{character}} advances to {range} range with {{target}}.".format(
                range=end_range
            ),
            mapping=dict(character=character,
                         target=target),
            exclude=(character, target)
        )
        return 1 * COMBAT_DELAY

    else:
        character.msg("You are unable to advance on {target}".format(
            target=target.get_display_name(character)
        ))
        return 0.2 * COMBAT_DELAY


def _do_retreat(character, _, args):
    """Implements the 'retreat' combat command."""
    combat_handler = character.ndb.combat_handler
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'ranged'
    start_range = combat_handler.get_min_range(character)

    ok = combat_handler.move_character(character, end_range, start_range)

    if ok:
        character.msg("You retreat from your enemies to {range} distance.".format(
            range=end_range
        ))
        character.location.msg_contents(
            "{{character}} retreats to {range} distance.".format(
                range=end_range
            ),
            mapping=dict(character=character),
            exclude=character
        )
    else:
        character.msg("You stumble in your attempt to retreat and are unable.")
        character.location.msg_contents(
            "{character} attempts to retreat but stumbles and is unable.",
            mapping=dict(character=character),
            exclude=character
        )

    return 1 * COMBAT_DELAY


def _do_flee(character, *args):
    """Implements the 'flee' combat command."""
    return 0 * COMBAT_DELAY


def process_next_action(combat_handler):
    """
    Callback that handles processing combat actions
    Args:
        combat_handler: instance of a combat handler

    Returns:
        None
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

        if duration > 1:
            # action takes more than one subturn; return it to the queue
            turn_actions[current_charid].append(
                (action, character, target, duration - 1)
            )
            combat_handler.db.actor_idx += 1
        else:
            args, action = action.split('/')[1:], action.split('/')[0]
            action_func = '_do_{}'.format(action)

            delay = globals()[action_func](character, target, args)
    else:
        combat_handler.db.actor_idx += 1

    utils.delay(delay, process_next_action, combat_handler)


def resolve_combat(combat_handler):
    """
    This is called by the combat handler
    actiondict is a dictionary with a list of two actions
    for each character:
    {char.id:[(action1, char, target, duration),
              (action2, char, target, duration)], ...}
    """

    combatants = combat_handler.db.characters

    # tiebreaker resolution helper function. super non-deterministic
    def _initiative_cmp(x, y):
        # first tiebreaker: result of the std_roll
        if x[2] != y[2]:
            return y[2] - x[2]
        else:
            # second tiebreaker: PCs before NPCs
            x_plyr, y_plyr = combatants[x[0]].has_player(), \
                             combatants[y[0]].has_player()
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

    # here, actor_idx is set to trigger the "end" of subturn 0
    # within the process_next_action call
    combat_handler.db.actor_idx = len(turn_order)

    # begin processing actions for characters in order
    process_next_action(combat_handler)

