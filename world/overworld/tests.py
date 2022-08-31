from evennia.utils.test_resources import EvenniaTest

from world.overworld import enter_overworld, OverworldMap, Overworld


class OverworldTestCase(EvenniaTest):
    def test_shows_map_right(self):
        height = 9
        width = 13
        symbols = OverworldMap.get_rect_symbols(-4, -6, width, height)
        rows = ["".join((symbol for symbol in row)) for row in symbols]

        tile_str = "\n".join(rows)

        print(tile_str)