"""
Chargen EvMenu module.
"""
from evennia.utils import fill
from world import archetypes, races, skills


def menunode_welcome_archetypes(caller):
    """Starting page and Archetype listing."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_select_archetype(caller, raw_input):
    """Archetype detail and selection menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_races(caller, raw_input):
    """Race listing menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_focuses(caller, raw_input):
    """Race detail and focus listing menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_select_race_focus(caller, raw_input):
    """Focus detail and final race/focus selection menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_allocate_traits(caller, raw_input):
    """Discretionary trait point allocation menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_allocate_mana(caller, raw_input):
    """Mana point allocation menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_allocate_skill_minuses(caller, raw_input):
    """Skill -1 counter allocation menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_allocate_skill_pluses(caller, raw_input):
    """Skill +1 counter allocation menu node."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_equipment(caller, raw_input):
    """Initial equipment "shopping"."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_examine_and_buy(caller, raw_input):
    """Examine and buy an item."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_character_desc(caller, raw_input):
    """Enter a character description."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_confirm(caller, raw_input):
    """Confirm and save allocations."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options
