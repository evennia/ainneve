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


COMBAT_DELAY = 2
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

    killer.msg("You have defeated {victim}".format(
        victim=victim
    ))
    killer.location.msg_contents(
        "{killer} has vanquished {victim}.",
        mapping={'killer': killer, 'victim': victim},
        exclude=(killer, victim))

    # award XP
    if victim.is_typeclass('typeclasses.characters.Character'):
        # in PVP, gain 10% of opponents XP
        xp_gained = int(floor(0.1 * victim.traits.XP.actual))
    else:
        # XP trait on NPCs contains the full award
        xp_gained = int(victim.traits.XP.actual)

    killer.traits.XP.base += xp_gained
    killer.msg("You gain {} XP".format(xp_gained))


def _do_nothing(character, _, args):
    """Default combat action if no action has been entered."""
    if 'continuing_1' in args:  # only message on the last repeat
        ch = character.ndb.combat_handler
        ch.combat_msg(
            ("Your attention wanders, despite the heated battle raging around you.",
             "{actor} stares into space vacantly."),
            actor=character)

        return 0.5 * COMBAT_DELAY
    else:
        return 0.2 * COMBAT_DELAY


def _do_drop(character, target, _):
    """Implement the 'drop item' combat action."""
    # drop the item and run hook
    target.move_to(character.location, quiet=True)
    if hasattr(target, 'at_drop'):
        target.at_drop(character)

    # messaging
    ch = character.ndb.combat_handler
    ch.combat_msg(
        ("You drop {item}.",
         "{actor} drops {item}."),
        actor=character,
        item=target)

    return 0.5 * COMBAT_DELAY


def _do_get(character, target, _):
    """Implement the 'get item' combat action."""
    if target in character.location.contents:
        # get the item and run hook
        target.move_to(character, quiet=True)
        if hasattr(target, 'at_get'):
            target.at_get(character)

        # messaging
        ch = character.ndb.combat_handler
        ch.combat_msg(
            ("You get {item}.",
             "{actor} gets {item}."),
            actor=character,
            item=target)

        return 1 * COMBAT_DELAY

    else:
        character.msg("You cannot get {}".format(target.get_display_name(character)))
        character.location.msg_contents(
            "{actor} searches around looking for something.",
            mapping={'actor': character}
        )
        return 0.5 * COMBAT_DELAY


def _do_equip(character, target, _):
    """Implement the 'equip' combat action, replacing any
    currently equipped item.
    """
    ch = character.ndb.combat_handler
    # handle swapping items if needed
    occupied_slots = [character.equip.get(s) for s in target.db.slots
                      if character.equip.get(s)]
    if occupied_slots:
        for item in occupied_slots:
            character.equip.remove(item)
            ch.combat_msg(
                ("You remove {item}",
                 "{actor} removes {item}."),
                actor=character,
                item=item)

    # equip the item and call hooks
    if not character.equip.add(target):
        ch.combat_msg(
            ("You can't equip {item}.",
             "{actor} looks at {item}, wasting precious time."),
            actor=character,
            item=target)

        return 0 * COMBAT_DELAY

    if hasattr(target, "at_equip"):
        target.at_equip(character)

    # messaging
    ch.combat_msg(
        ("You equip {item}",
         "{actor} equips {item}."),
        actor=character,
        item=target)

    return 1 * COMBAT_DELAY


def _do_attack(character, target, args):
    """Implement melee and ranged 'attack' ch actions."""
    ch = character.ndb.combat_handler

    # confirm the target is still in combat
    if not target.id in ch.db.characters:
        ch.combat_msg(
            ("You are unable to attack {defender}.",
             "{actor} is unable to attack {defender}."),
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
        damage = (atk_roll + character.traits.ATKM) - target.traits.DEF

    else:  # attack_type == 'ranged'
        # confirm we have proper ammunition
        ammunition = weapon.get_ammunition_to_fire()

        if not ammunition:
            ch.combat_msg(
                ("You do not have any {ammo}s",
                 "{actor}'s quiver has no more {ammo}s"),
                actor=character,
                ammo=weapon.db.ammunition)
            return 0

        # calculate damage
        damage = (atk_roll + character.traits.ATKR) - target.traits.DEF

    # apply damage
    if damage > 0:
        if ammunition:
            # ammunition goes into target
            ammunition.move_to(target, quiet=True)

        if dodging:
            ch.combat_msg(
                ("You try to dodge the incoming attack, but",
                 "{actor} tries to dodge, but"),
                actor=target)

        if any((arg.startswith('s') for arg in args)):
            # 'subdue': deduct stamina instead of health
            target.traits.SP.current -= damage
            status = 'dmg_sp'

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

    if attack_range == 'reach' and attack_type == 'ranged':
        # remove the range bonus
        character.traits.ATKR.mod -= 1

    return 1 * COMBAT_DELAY


def _do_kick(character, target, args):
    """Implements the 'kick' combat command."""
    ch = character.ndb.combat_handler
    if not any(arg.startswith('continuing') for arg in args):
        if character.db.position != 'STANDING':
            # if you are in any wrestling position other
            # than free standing, all you can do is wrestle to break free
            return _do_wrestle(character, target, ['break'])

        # two-phase action - first turn; messaging only
        ch.combat_msg(
            ("You take a step toward {target}.",
             "{actor} takes a step toward {target}.",
             "{actor} takes a step toward you."),
            actor=character,
            target=target)

    else:
        # confirm the target is still in combat
        # and is within range
        attack_range = ch.get_range(character, target)
        if target.id not in ch.db.characters \
                or attack_range != 'melee':
            ch.combat_msg(
                ("You are unable to kick {defender}.",
                 "{actor} is unable to kick {defender}."),
                actor=character,
                defender=target)

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
                    ("You try to dodge the incoming attack, but",
                     "{actor} tries to dodge, but"),
                    actor=target
                )

            if any((arg.startswith('s') for arg in args)):
                # 'subdue': deduct stamina instead of health
                target.traits.SP.current -= damage
                status = 'dmg_sp'

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
            'dmg_hp': ("You kick {target} savagely, sending them reeling.",
                       "{actor} kicks {target} savagely, sending them reeling.",
                       "{actor} kicks you savagely, sending you reeling."),
            'dmg_sp': ("You kick {target} squarely in the chest, bringing them "
                       "closer to submission.",
                       "{actor} kicks {target} squarely in the chest, and {target} "
                       "staggers from the blow.",
                       "{actor} kicks you hard in the chest and you feel your "
                       "resolve weaken."),
            'dodged': ("You attempt to kick {target}, but they dodge, leaving you "
                       "off balance.",
                       "{target} dodges a kick from {actor}, throwing {actor} off balance.",
                       "{actor} attempts to kick you, but you duck to one side."),
            'missed': ("You kick at {target} with all your might, but fail to connect, "
                       "throwing you off balance.",
                       "{actor} kicks toward {target} and misses.",
                       "{actor} tries to kick you but misses, falling off balance.")
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


def _do_strike(character, target, args):
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
            ("You are too far to strike {defender}.",
             "{actor} is to far away from {defender} to strike them."),
            actor=character,
            defender=target)
        return 0.2 * COMBAT_DELAY

    # and has at least one free hand
    strikes = sum(1 if character.equip.get(slot) is None else 0
                  for slot in character.db.slots
                  if slot.startswith('wield'))
    if strikes <= 0:
        ch.combat_msg(
            ("You do not have a free hand.",
             "{actor} goes to punch, but does not have a free hand."),
            actor=character)
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
                ("You try to dodge the incoming attack, but",
                 "{actor} tries to dodge, but"),
                actor=target
            )

        if any((arg.startswith('s') for arg in args)):
            # 'subdue': deduct stamina instead of health
            target.traits.SP.current -= damage
            status = 'dmg_sp'

        else:
            target.traits.HP.current -= damage
            status = 'dmg_hp'
    else:
        if dodging:
            status = 'dodged'
        else:
            status = 'missed'

    messages = {
        'dmg_hp': ("You strike {target} savagely with your fist.",
                   "{actor} strikes {target} savagely with their fist.",
                   "{actor} strikes you savagely with their fist."),
        'dmg_sp': ("You strike {target} hard in the chest, bringing them "
                   "closer to submission.",
                   "{actor} strikes {target} hard in the chest, and {target} "
                   "staggers from the blow.",
                   "{actor} strikes you hard in the chest and you feel your "
                   "resolve weaken."),
        'dodged': ("You attempt to strike {target}, but they dodge the punch.",
                   "{target} dodges a punch from {actor}.",
                   "{actor} attempts to strike you, but you dodge it easily."),
        'missed': ("You attempt to strike {target} with all your might, but "
                   "your fist fails to connect",
                   "{actor} attempts to punch {target} and misses.",
                   "{actor} tries to punch you but misses.")
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
            utils.delay(0.5 * COMBAT_DELAY, _do_strike, character, target, args)

        return 1 * COMBAT_DELAY


def _do_advance(character, target, args):
    """Implements the 'advance' combat command."""
    ch = character.ndb.combat_handler
    start_range = ch.get_range(character, target)
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'melee'

    if start_range == end_range:
        character.msg("You are already at {range} with {target}.".format(
            range=end_range,
            target=target.get_display_name(character)
        ))
        return 0.2 * COMBAT_DELAY

    ok = ch.move_character(character, end_range, start_range, target)

    if ok:
        ch.combat_msg(
            ("You advance on {target} to {range} range.",
             "{actor} advances to {range} range with {target}.",
             "{actor} advances on you to {range} range."),
            actor=character,
            target=target,
            range=end_range)

        return 1 * COMBAT_DELAY

    else:
        character.msg("You are unable to advance on {target}".format(
            target=target.get_display_name(character)
        ))
        character.location.msg_contents(
            "{actor} stumbles and fails to move.",
            mapping={'actor': character},
            exclude=character
        )
        return 0.5 * COMBAT_DELAY


def _do_retreat(character, _, args):
    """Implements the 'retreat' combat command."""
    ch = character.ndb.combat_handler
    end_range = 'reach' if any(arg.startswith('r') for arg in args) \
                    else 'ranged'
    start_range = ch.get_min_range(character)

    ok = ch.move_character(character, end_range, start_range)

    if ok:
        ch.combat_msg(
            ("You retreat from your enemies to {range} distance.",
             "{actor} retreats to {range} distance."),
            actor=character,
            range=end_range)
    else:
        ch.combat_msg(
            ("You stumble in your attempt to retreat and are unable.",
             "{actor} attempts to retreat but stumbles and is unable."),
            actor=character)

    return 1 * COMBAT_DELAY


def _do_dodge(*args):
    """Dodging is handled in attack actions. This is essentially a placeholder."""
    return 0


def _do_flee(character, _, args):
    """Implements the 'flee' combat command."""
    ch = character.ndb.combat_handler
    if not any(arg.startswith("continuing") for arg in args):
        ch.combat_msg(
            ("You begin to search desperately for an escape route.",
             "{actor} looks about frantically."),
            actor=character)
    else:
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
            ch.remove_character(character)
            ch.combat_msg(
                ("You slip through your enemies' fingers and escape!",
                 "{actor} seizes the opportunity to escape the fight!"),
                actor=character)

            # prevent re-attack for a time
            character.ndb.no_attack = True
            safe_time = 2 * (character.skills.escape + d_roll('1d6'))

            def enable_attack():
                del character.ndb.no_attack

            utils.delay(safe_time, enable_attack)
        else:
            # failed to escape
            ch.combat_msg(
                ("You are locked in close combat and cannot get away.",
                 "{actor} looks around frantically for an escape route, but is boxed in."),
                actor=character)

    return 1 * COMBAT_DELAY


def _do_wrestle(character, target, args):
    """Implements the 'wrestle' combat command."""
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
                ('{}/continuing_{}'.format(action, duration - 1),
                 character,
                 target,
                 duration - 1)
            )
            combat_handler.db.actor_idx += 1

        args, action = action.split('/')[1:], action.split('/')[0]
        action_func = '_do_{}'.format(action)

        delay = globals()[action_func](character, target, args)
    else:
        combat_handler.db.actor_idx += 1

    if len(combat_handler.db.characters) < 2:
        combat_handler.stop()
    else:
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

