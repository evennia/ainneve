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

import re, random


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


def resolve_combat(combat_handler, actiondict):
    """
    This is called by the combat handler
    actiondict is a dictionary with a list of two actions
    for each character:
    {char.id:[(action1, char, target, duration),
              (action2, char, target, duration)], ...}
    """
    from pprint import pformat
    combat_handler.msg_all(pformat(actiondict))
    return
    # combatants = combat_handler.db.characters
    #
    # # tiebreaker resolution helper function. super non-deterministic
    # def _initiative_cmp(x, y):
    #     # first tiebreaker: result of the std_roll
    #     if x[2] == y[2]:
    #         # second tiebreaker: PCs before NPCs
    #         x_plyr, y_plyr = combatants[x[0]].has_player(), \
    #                          combatants[y[0]].has_player()
    #         if x_plyr and not y_plyr:
    #             return 1
    #         elif y_plyr and not x_plyr:
    #             return -1
    #         else:
    #             # third tiebreaker: reroll
    #             roll_x = std_roll() + combatants[x[0]].traits.PER.actual
    #             roll_y = std_roll() + combatants[y[0]].traits.PER.actual
    #             if roll_x != roll_y:
    #                 return roll_x - roll_y
    #             else:
    #                 return random.choice((-1, 1))
    #     else:
    #         return y[2] - x[2]
    #
    # # Do the Initiative roll to determine turn order
    # turn_order = []
    # intv_rolls = {}
    # for combatant in combatants.values():
    #     roll = std_roll()
    #     initiative = roll + combatant.traits.PER.actual
    #     if initiative in intv_rolls:
    #         intv_rolls[initiative].append((combatant.id, initiative, roll))
    #     else:
    #         intv_rolls[initiative] = [(combatant.id, initiative, roll)]
    #
    # # resolve ties and build the turn order
    # for intv in sorted(intv_rolls, reverse=True):
    #     if len(intv_rolls[intv]) == 1:
    #         turn_order += intv_rolls[intv][0]
    #     else:  # more than one rolled same Initiative
    #         turn_order += sorted(intv_rolls[intv], cmp=_initiative_cmp)
    #
    # # process actions for characters in order
    # for dbref, _, _ in turn_order:
    #     pass
    #
