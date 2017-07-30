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
