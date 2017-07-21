"""
Utility objects.
"""
from evennia import TICKER_HANDLER as tickerhandler
from world import archetypes, races, skills


def sample_char(char, archetype, race, focus=None):
    """Loads sample traits onto a character.

    Args:
        char (Character): character to load traits
        archetype (str): name of base archetype
        race (str): name of race to become
        focus Optional(str): focus to apply. if None, default is race's
            first item in foci collection
        """
    archetypes.apply_archetype(char, archetype, reset=True)
    char.traits.STR.base += 1
    char.traits.PER.base += 1
    char.traits.INT.base += 1
    char.traits.DEX.base += 1
    char.traits.CHA.base += 1
    char.traits.VIT.base += 2
    char.traits.MAG.base += 2
    focus = focus or races.load_race(race).foci[0]
    races.apply_race(char, race, focus)
    archetypes.calculate_secondary_traits(char.traits)
    archetypes.finalize_traits(char.traits)
    tickerhandler.add(interval=6, callback=char.at_turn_start)
    skills.apply_skills(char)
    skills.finalize_skills(char.skills)


def call_immediate(delay, callback, *args, **kwargs):
    """utility function to be patched in place of ...utils.delay for testing"""
    callback(*args, **kwargs)

EXIT_OFFSETS = {
    # up is negative
    #     ( x,  y)
    'n' : (+0, -1),
    'ne': (+1, -1),
    'e' : (+1, +0),
    'se': (+1, +1),
    's' : (+0, +1),
    'sw': (-1, +1),
    'w' : (-1, +0),
    'nw': (-1, -1),
}
EXIT_NAME_MAPPINGS = {
    'north': 'n',
    'east': 'e',
    'south': 's',
    'west': 'w',
}
def shorten_name(name):
    for long, short in EXIT_NAME_MAPPINGS.items():
        name = name.replace(long, short)
    return name

def offset_for_exit(exit):
    names = []
    exit.at_cmdset_get() # load the exit command if needed
    for command in exit.cmdset.current:
        command_names = [command.key]
        command_names.extend(command.aliases)
        for name in command_names:
            if name in EXIT_OFFSETS:
                names.append(name)
            else:
                names.append(shorten_name(name))
    for name in names:
        if name in EXIT_OFFSETS:
            return EXIT_OFFSETS[name] # Please don't name an exit with two directions
    return False

def get_directed_exits(room):
    directed_exits = {}
    for exit in room.exits:
        offset = offset_for_exit(exit)
        if offset:
            directed_exits[exit.destination] = offset
    return directed_exits
