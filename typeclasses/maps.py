# -*- encoding: utf-8 -*-

from items import Item
from utils import utils

TILES = {
    'WATER': u'≈≈≈',
    'DEEPWATER': u'≋≋≋',
    'VEGETATION': u'~↟~',
    'GRASS': u' . ',
}
CELL_WIDTH = 3
PADDING = 1

class Map(Item):
    '''
    The Map typeclass creates an empty map which fills up
    as its owner travels through Ainneve.
    When looking at the map, a representation of the world
    as explored so far is shown.

    Rooms can customize the map tile drawn for them in several ways:
        - by specifying a `map_tile()` function that takes the requesting map
          and returns a three-character string to draw on the map
        - by specifying a `map_tile` property containing
          a three-character string to draw on the map
        - by specifying a `map_tile` Attribute containing
          a three-character string to draw on the map
        - by specifying a `terrain` present in the TILES dictionary in maps.py
    If no tile can be found, the map will display `?!?` as the tile.
    '''
    weight = 1.0

    def at_object_creation(self):
        super(Map, self).at_object_creation()
        self.db.map_data = {}
        self.db.x = self.db.y = 0
        self.db.off_map = False
        self.map_current_room()

    @property
    def room(self):
        '''
        Finds the room that this object is currently in,
        or None if it isn’t in a room.
        This still works if the map is inside one or more nested objects.
        '''
        loc = self.location
        if loc is None:
            return loc

        done = False
        while 1:
            if loc.location is not None:
                loc = loc.location
            else:
                break
        return loc

    @property
    def current_character(self):
        '''
        This returns the character carrying the map,
        or None if the map isn’t currently being carried by a character.
        '''
        character = self.location
        if character is None:
            return character

        done = False
        while 1:
            if character is None:
                return None
            if character.player is None:
                character = character.location
            else:
                break
        return character

    def draw_map(self, show_player = True):
        '''
        This returns a two-dimensional list containing the map tiles.

        If the owner is a builder, the map displays rows
        containing the DB numbers for each room above each row.

        If the show_player argument is `True`, the room the owning player
        is currently in will have its middle character replaced with a `*`.
        '''
        player = self.current_character.player
        is_builder = player.locks.check_lockstring(player, 'dummy:perm(Builders)')

        min_x = max_x = 0
        min_y = max_y = 0
        for room_info in self.db.map_data.values():
            x = room_info['x']
            y = room_info['y']
            if x < min_x: min_x = x
            if y < min_y: min_y = y
            if x > max_x: max_x = x
            if y > max_y: max_y = y

        max_x += 1
        max_y += 1

        width = max_x - min_x
        height = max_y - min_y

        alt_grid = None
        if is_builder:
            alt_grid = []
            for y in range(height):
                alt_grid.append([])
                for x in range(width):
                    alt_grid[y].append(' ' * CELL_WIDTH)
            for room, room_info in self.db.map_data.items():
                alt_grid[room_info['y'] - min_y][room_info['x'] - min_x] = str(room.id).center(CELL_WIDTH)


        map_grid = []
        for y in range(height):
            map_grid.append([])
            for x in range(width):
                map_grid[y].append(' ' * CELL_WIDTH)
        for room, room_info in self.db.map_data.items():
            map_grid[room_info['y'] - min_y][room_info['x'] - min_x] = self.tile_for_room(room)

        if show_player and not self.db.off_map:
            x = self.db.x - min_x
            y = self.db.y - min_y
            try:
                tile = list(map_grid[y][x])
            except IndexError: pass
            else:
                tile[int(len(tile) / 2)] = '*'
                map_grid[y][x] = ''.join(tile)

        if alt_grid:
            for i, row in reversed(list(enumerate(alt_grid))):
                map_grid.insert(i, row)
        return map_grid

    def tile_for_room(self, room):
        '''
        Get the tile for the provided `room`,
        or `?!?` if no tile could be found.
        '''
        tile = None
        try:
            tile = room.map_tile
        except AttributeError: pass
        else:
            tile = room.map_tile(self)

        if tile is None:
            tile = room.db.map_tile
        if tile is None:
            tile = TILES.get(room.terrain, '?!?')

        return tile


    def return_appearance(self, looker):
        '''
        Return the map data nicely wrapped up in a box:
        ┌─── MAP ───┐
        │ map  here │
        └───────────┘
        '''
        map_grid = self.draw_map()
        width = CELL_WIDTH * len(map_grid[0]) + PADDING * 2

        map_page = []
        title_line = title = u' MAP '
        # str.center is dumb. Work around that.
        spacer = u'─'
        i = 0
        while len(title_line) < width:
            if i % 2:
                title_line += spacer
            else:
                title_line = spacer + title_line
            i += 1
        map_page.append(u'┌' + title_line + u'┐')
        padding = ' ' * PADDING
        for line in map_grid:
            map_page.append(u'│' + padding + ''.join(line) + padding + u'│')
        map_page.append(u'└' + u'─' * max(width, len(title)) + u'┘')
        return '\n'.join(map_page)

    def map_current_room(self):
        '''
        Add the room the map is currently in to the map,
        including any rooms directly visible through the exits.
        '''
        if self.db.off_map: self.at_enter_map()
        self.map_room(self.room, self.db.x, self.db.y)
        for dest, (dx, dy) in utils.get_directed_exits(self.room).items():
            self.map_room(dest, self.db.x + dx, self.db.y + dy)

    def map_room(self, room, x, y):
        '''
        Add only the provided room (at coordinates (x, y)) to the map.
        '''
        if room not in self.db.map_data:
            self.db.map_data[room] = {}
        self.db.map_data[room].update({
            'x': x,
            'y': y,
        })

    def at_enter_map(self):
        self.current_character.msg('You’re back on the map.')
        self.db.off_map = False

    def at_leave_map(self):
        self.current_character.msg('Can’t fit this into the map.')
        self.db.off_map = True

    def parent_did_move_from(self, source_location, exit=None):
        '''
        Called immediately after the holding object moves to a new room.

        `source_location` is where the holder came from.
        `exit` is the exit if any that the holder just traversed.

        Note: If the exit is not a recognized direction,
              the map will not update until the user returns
              to an already-mapped room.
        '''
        new_room = self.room
        if new_room in self.db.map_data:
            info = self.db.map_data[new_room]
            self.db.x = info['x']
            self.db.y = info['y']
            self.map_current_room()
        elif exit is not None:
            offset = utils.offset_for_exit(exit)
            if offset and not self.db.off_map:
                dx, dy = offset
                self.db.x += dx
                self.db.y += dy
                self.map_current_room()
            else:
                self.at_leave_map()
        else:
            self.at_leave_map()
