from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterClass:
    key: str
    name: str
    desc: str
    primary_stat: str
    secondary_stat: str
    health_dice: tuple[int, int]
    mana_dice: tuple[int, int]

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
        health_dice=(1, 10),
        mana_dice=(1, 6),
    )

    Paladin = CharacterClass(
        key="paladin",
        name="Paladin",
        primary_stat="strength",
        secondary_stat="will",
        desc="Strong in melee combat with some divine spells.",
        health_dice=(1, 10),
        mana_dice=(1, 6),
    )

    Rogue = CharacterClass(
        key="rogue",
        name="Rogue",
        primary_stat="cunning",
        secondary_stat="strength",
        desc="Adept fighter relying on stealthy tactics and evasion.",
        health_dice=(1, 8),
        mana_dice=(1, 8),
    )

    Bard = CharacterClass(
        key="bard",
        name="Bard",
        primary_stat="cunning",
        secondary_stat="will",
        desc="Able to buff allies and debuff enemies while being able to contribute in combat.",
        health_dice=(1, 8),
        mana_dice=(1, 8),
    )

    Shaman = CharacterClass(
        key="shaman",
        name="Shaman",
        primary_stat="will",
        secondary_stat="strength",
        desc="Good caster capable of fighting with heavy weapons.",
        health_dice=(1, 6),
        mana_dice=(1, 10),
    )

    Wizard = CharacterClass(
        key="wizard",
        name="Wizard",
        primary_stat="will",
        secondary_stat="cunning",
        desc="Focused caster.",
        health_dice=(1, 6),
        mana_dice=(1, 10),
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