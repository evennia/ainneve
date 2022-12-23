from dataclasses import dataclass


@dataclass(frozen=True)
class Race:
    key: str
    name: str
    desc: str
    strength_mod: int = 0
    cunning_mod: int = 0
    will_mod: int = 0

    def __str__(self):
        return self.name


# TODO Write good descriptions


class Races:
    _cached_dict = None

    Human = Race(
        key="human",
        name="Human",
        cunning_mod=1,
        desc="Your average human.",
    )

    Dwarf = Race(
        key="dwarf",
        name="Dwarf",
        strength_mod=1,
        desc="Short and strong.",
    )

    HalfElf = Race(
        key="half_elf",
        name="Half Elf",
        will_mod=1,
        desc="Bit less average"
    )

    Elf = Race(
        key="elf",
        name="Elf",
        strength_mod=-1,
        will_mod=1,
        desc="Regular elves",
    )

    Goblin = Race(
        key="goblin",
        name="Goblin",
        cunning_mod=1,
        strength_mod=-1,
        will_mod=1,
        desc="Small and cunning"
    )

    Orc = Race(
        key="orc",
        name="Orc",
        strength_mod=2,
        will_mod=-1,
        desc="Tall and strong",
    )

    Lizardman = Race(
        key="lizardman",
        name="Lizardman",
        cunning_mod=1,
        strength_mod=1,
        will_mod=-1,
        desc="Reptilian hunters"
    )

    Ratman = Race(
        key="ratman",
        name="Ratman",
        cunning_mod=2,
        strength_mod=-1,
        desc="Shorter but cunning"
    )

    @classmethod
    def _get_cached_dict(cls):
        if not cls._cached_dict:
            new_dict = {value.key: value for value in cls.__dict__.values() if isinstance(value, Race)}
            cls._cached_dict = new_dict

        return cls._cached_dict

    @classmethod
    def items(cls):
        return cls._get_cached_dict().items()

    @classmethod
    def values(cls):
        return cls._get_cached_dict().values()

    @classmethod
    def get(cls, key):
        return cls._get_cached_dict().get(key)
