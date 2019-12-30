"""
Races module.

This module contains data and functions relating to Races and Focuses. Its
public module functions are to be used primarily during the character
creation process.

Classes:

    `Race`: base class for all races
    `Human`: human race class
    `Elf`: elf race class
    `Dwarf`: dwarf race class
    `Focus`: class representing a character's focus; a set of bonuses

Module Functions:

    - `load_race(str)`:

        loads an instance of the named Race class

    - `load_focus(str)`:

        loads an instance of the named Focus class

    - `apply_race(char, race, focus)`:

        have a character "become" a member of the specified race with
        the specified focus
"""

from evennia.utils import fill
from world.archetypes import Archetype


class RaceException(Exception):
    """Base exception class for races module."""
    def __init__(self, msg):
        self.msg = msg

ALL_RACES = ('Human', 'Elf', 'Dwarf')
_ALL_FOCI = {
    'agility':
        {'desc': 'The Agility focus represents an increase in nimbleness, '
                 'flexibility, and balance. Characters with the agility '
                 'focus have trained their body to become more acrobatic, '
                 'and therefore stronger.',
         'bonuses':
             {'STR': 1, 'DEX': 2, 'REFL': 2}},
    'alertness':
        {'desc': 'The Alertness focus represents increased senses, awareness, '
                 'and insight. Characters with the alertness focus are keenly '
                 'aware of their surroundings and possible dangers.',
         'bonuses':
             {'PER': 2, 'CHA': 1, 'REFL': 2}},  # +2 language
    'brawn':
        {'desc': 'The Brawn focus is for characters with exceptionally '
                 'strong bodies. Constant training has earned characters with '
                 'the brawn focus large muscles and great physical power.',
         'bonuses':
             {'STR': 2, 'VIT': 1, 'FORT': 1}},
    'cunning':
        {'desc': 'The Cunning focus represents intelligent, clever, and '
                 'quick-witted characters. Characters with the cunning focus '
                 'are extremely bright and spend much of their time studying '
                 'and developing new skills.',
         'bonuses':
             {'PER': 1, 'INT': 2, 'WILL': 3}},
    'prestige':
        {'desc': 'The Prestige focus symbolizes characters who are great '
                 'speech givers, negotiators, and magnetic personalities. '
                 'Characters with the prestige focus can win the hearts and '
                 'minds of their peers and pull strings for favors.',
         'bonuses':
             {'INT': 1, 'CHA': 2}},  # + 3 language
    'resilience':
        {'desc': 'The Resilience focus is for characters with naturally '
                 'strong constitutions and fortitudes. Characters with the '
                 'resilience focus tend to have longer life spans and live '
                 'healthier lives.',
         'bonuses':
             {'DEX': 1, 'VIT': 2, 'FORT': 3, 'WILL': 2}},
    'spirit': {
        'desc': 'The Spirit focus symbolizes an abundance in mystical powers '
                'swirling with mana. Characters with the spirit focus are '
                'naturally gifted to channelling the magical powers of spells.',
        'bonuses':
            {'VIT': 1, 'MAG': 2, 'FORT': 1, 'REFL': 1, 'WILL': 1}}  # +2 language
}
_ARC = Archetype()


def load_race(race):
    """Returns an instance of the named race class.

    Args:
        race (str): case-insensitive name of race to load

    Returns:
        (Race): instance of the appropriate subclass of `Race`
    """
    race = race.capitalize()
    if race in ALL_RACES:
        return globals()[race]()
    else:
        raise RaceException("Invalid race specified.")


def load_focus(focus):
    """Retrieve an instance of a Focus class.

    Args:
        focus (str): case insensitive focus class name

    Returns:
        (Focus): instance of the named Focus
    """
    focus = focus.lower()
    if focus in _ALL_FOCI:
        return Focus(name=focus, **_ALL_FOCI[focus])
    else:
        raise RaceException('Invalid Focus name.')


def apply_race(char, race, focus):
    """Causes a Character to "become" the named race.

    Args:
        char (Character): the character object becoming a member of race
        race (str, Race): the name of the race to apply, or the
        focus (str, Focus): the name of the focus the player has selected
    """
    # if objects are passed in, reload Race and Focus objects
    # by name to ensure we have un-modified versions of them
    if isinstance(race, Race):
        race = race.name

    race = load_race(race)

    if isinstance(focus, Focus):
        focus = focus.name

    focus = load_focus(focus)

    # make sure the focus is allowed for the race
    if focus.name not in (f.name for f in race.foci):
        raise RaceException(
            'Invalid focus specified. '
            'Focus {} not available to race {}.'.format(focus.name, race.name)
        )

    # set race and related attributes on the character
    char.db.race = race.name
    char.db.focus = focus.name
    char.db.slots = race.slots
    char.db.limbs = race.limbs

    # apply race-based bonuses
    for trait, bonus in race.bonuses.items():
        char.traits[trait].mod += bonus
    # apply focus-based bonuses
    for trait, bonus in focus.bonuses.items():
        char.traits[trait].mod += bonus


def _format_bonuses(bonuses):
    """Formats a dict of bonuses to base traits as a string."""
    traits = list(bonuses.keys())
    if len(bonuses) > 2:
        output = ", ".join(
                    "|w{:+1}|n to |C{}|n".format(bonuses[t],
                                                     _ARC.traits[t]['name'])
                    for t in traits[:-1])
        output += ", and |w{:+1}|n to |C{}|n".format(
                      bonuses[traits[-1]],
                      _ARC.traits[traits[-1]]['name'])
    else:
        output = " and ".join(
                    "|w{:+1}|n to |C{}|n".format(bonuses[t],
                                                     _ARC.traits[t]['name'])
                    for t in traits)
    return output


class Race(object):
    """Base class for race attributes"""
    def __init__(self):
        self.name = ""
        self.plural = ""
        self.size = ""
        self._desc = ""
        self.slots = {
            'wield1': None,
            'wield2': None,
            'armor': None,
        }
        self.limbs = (
            ('r_arm', ('wield1',)),
            ('l_arm', ('wield2',)),
            ('body', ('armor',)),
        )
        self.foci = []
        self.bonuses = {}

    @property
    def desc(self):
        """Returns a formatted description of the Race.

        Note:
            The setter for this property only modifies the content
            of the first paragraph of what is returned.
        """
        desc = "|g{}|n\n".format(self.name)
        desc += fill(self._desc)
        desc += '\n\n'
        desc += fill("{} have a ".format(self.plural) +
                     "|y{}|n body type and can ".format(self.size) +
                     "select a |wfocus|n from among {}".format(
                         self._format_focus_list(self.foci)
                     ))
        if len(self.bonuses) > 0:
            desc += '\n\n'
            desc += fill("{} also gain {} of {}".format(
                        self.plural,
                        'bonuses' if len(self.bonuses) > 1 else 'a bonus',
                        _format_bonuses(self.bonuses))
                    )
        desc += '\n\n'
        return desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    def _format_focus_list(self, items):
        """Returns a comma separated list of items with "or" before the last."""
        if len(items) > 2:
            output = ", ".join(["|b{}|n".format(i.name) for i in items[:-1]])
            output += ", or |b{}|n".format(items[-1].name)
        else:
            output = " or ".join(["|b{}|n".format(i.name) for i in items])
        return output


class Focus(object):
    """Represents a Focus, which is a group of bonuses available to a race.

    Args:
        name (str): display name for the focus
        desc (str): description for the focus
        bonuses (dict): bonuses for the focus in {'trait': bonus} format
    """
    def __init__(self, name, desc, bonuses):
        self.name = name.capitalize()
        self._desc = None
        self.desc = desc
        self.bonuses = bonuses

    @property
    def desc(self):
        """Returns a formatted description of the Focus.

        Note:
            The setter for this property only modifies the content
            of the first paragraph of what is returned.
        """
        desc = "|b{}|n\n".format(self.name)
        desc += fill(self._desc)
        desc += "\n\n"
        desc += fill("Adventurers with the |b{}|n focus gain {}.".format(
                    self.name,
                    _format_bonuses(self.bonuses)
                ))
        desc += "\n\n"
        return desc

    @desc.setter
    def desc(self, value):
        self._desc = value


class Human(Race):
    """Class representing human attributes."""
    def __init__(self):
        super(Human, self).__init__()
        self.name = "Human"
        self.plural = "Humans"
        self.size = "medium"
        self.desc = ("|gHumans|n are the most widespread of all the races. "
                     "The human traits of curiosity, resourcefulness and "
                     "unyielding courage have helped them to adapt, survive "
                     "and prosper in every world they have explored.")
        self.foci = [load_focus(f) for f
                     in ('agility', 'cunning', 'prestige')]
        self.bonuses = {'WILL': 1}  # +3 languages


class Elf(Race):
    """Class representing elf attributes."""
    def __init__(self):
        super(Elf, self).__init__()
        self.name = "Elf"
        self.plural = "Elves"
        self.size = "medium"
        self.desc = ("|gElves|n are graceful, slender demi-humans with delicate "
                     "features and pointy ears. Elves are known to use magic "
                     "spells, but prefer to spend their time feasting and "
                     "frolicking in wooded glades. They rarely visit cities of "
                     "men. Elves are fascinated by magic and never grow weary "
                     "of collecting spells or magic items. Elves love "
                     "beautifully crafted items and choose to live an agrarian "
                     "life in accord with nature. ")
        self.foci = [load_focus(f) for f
                     in ('agility', 'spirit', 'alertness')]
        self.bonuses = {}


class Dwarf(Race):
    """Class representing dwarf attributes."""
    def __init__(self):
        super(Dwarf, self).__init__()
        self.name = "Dwarf"
        self.plural = "Dwarves"
        self.size = "small"
        self.desc = ("|gDwarves|n are short, stocky demi-humans with long, "
                     "respectable beards and heavy stout bodies. Their skin "
                     "is earthen toned and their hair black, gray or dark "
                     "brown. Stubborn but practical; dwarves love grand "
                     "feasts and strong ale. They can be dangerous opponents, "
                     "able to fight with any weapon, melee or ranged. They "
                     "admire craftsmanship and are fond of gold and stonework. "
                     "Dwarves are dependable fighters and sturdy against "
                     "magical influences. ")
        self.foci = [load_focus(f) for f
                     in ('brawn', 'resilience', 'alertness')]
        self.bonuses = {'WILL': 1}
