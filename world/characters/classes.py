from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterClass:
    key: str
    name: str
    desc: str
    primary_stat: str
    secondary_stat: str

    def __str__(self):
        return self.name


# TODO Write good descriptions


class CharacterClasses:
    _cached_dict = None

    Warrior = CharacterClass(
        key="warrior",
        name="Warrior",
        primary_stat="strength",
        secondary_stat="cunning",
        desc="Very strong in melee combat.",
    )

    Paladin = CharacterClass(
        key="paladin",
        name="Paladin",
        primary_stat="strength",
        secondary_stat="will",
        desc="Strong in melee combat with some divine spells.",
    )

    Rogue = CharacterClass(
        key="rogue",
        name="Rogue",
        primary_stat="cunning",
        secondary_stat="strength",
        desc="Adept fighter relying on stealthy tactics and evasion.",
    )

    Bard = CharacterClass(
        key="bard",
        name="Bard",
        primary_stat="cunning",
        secondary_stat="will",
        desc="Able to buff allies and debuff enemies while being able to contribute in combat.",
    )

    Shaman = CharacterClass(
        key="shaman",
        name="Shaman",
        primary_stat="will",
        secondary_stat="strength",
        desc="Good caster capable of fighting with heavy weapons.",
    )

    Wizard = CharacterClass(
        key="wizard",
        name="Wizard",
        primary_stat="will",
        secondary_stat="cunning",
        desc="Focused caster.",
    )

    @classmethod
    def _get_cached_dict(cls):
        if not cls._cached_dict:
            new_dict = {value.key: value for value in cls.__dict__.values() if isinstance(value, CharacterClass)}
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