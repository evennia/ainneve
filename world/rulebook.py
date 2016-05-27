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

from random import randint
import re


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

    rolls = [randint(1, die) for _ in range(num)]

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
