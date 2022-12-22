"""
Tiles are used to shape the Overworld room.
They are mapped using the symbol and will only show up if there are no landmarks.
To add new ones you only need to add a Tile instance in the OverworldTiles class.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    name: str
    symbol: str
    room_prototype: str
    alt_symbols: tuple = tuple()
    # Other random tables could be here, like possible encounters


class OverworldTiles:
    """ Simple class acting as repository for the tiles """

    _cached_dict = None

    Mountains = Tile(
        name="Mountains",
        symbol='λ',
        room_prototype="wilderness_mountains"
    )

    Water = Tile(
        name="Water",
        symbol='≈',
        room_prototype="wilderness_water"
    )

    Swamp = Tile(
        name="Swamp",
        symbol='▒',
        room_prototype="wilderness_swamp"
    )

    Desert = Tile(
        name="Desert",
        symbol='░',
        room_prototype="wilderness_desert"
    )

    Trees = Tile(
        name="Trees",
        symbol='ǂ',
        room_prototype="wilderness_trees"
    )

    Bridge = Tile(
        name="Bridge",
        symbol='Ξ',
        room_prototype="wilderness_bridge"
    )

    Plains = Tile(
        name="Plains",
        symbol='.',
        room_prototype="wilderness_plains"
    )

    Canyon = Tile(
        name="Canyon",
        symbol='Ų',
        room_prototype="wilderness_canyon",
    )

    Road = Tile(
        name="Road",
        symbol='═',
        room_prototype="wilderness_road",
        alt_symbols=("║", "╦", "╔", "╗", "╚", "╝", "╣", "╠")
    )

    City = Tile(
        name="City",
        symbol='[∆]',
        room_prototype="wilderness_city"
    )

    Mystery = Tile(
        name="Mystery",
        symbol='(?)',
        room_prototype="wilderness_mystery"
    )

    @classmethod
    def _get_cached_dict(cls):
        if not cls._cached_dict:
            new_dict = {key: value for key, value in cls.__dict__.items() if isinstance(value, Tile)}
            cls._cached_dict = new_dict

        return cls._cached_dict

    @classmethod
    def items(cls):
        return cls._get_cached_dict().items()

    @classmethod
    def values(cls):
        return cls._get_cached_dict().values()
