import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typeclasses.characters import BaseCharacter


class _NextLevelXp:
    """
    Dataclass to make our mapping of levels to xp more readable.
    """
    __slots__ = ('level', 'xp_per_level')

    def __init__(self, level, xp_per_level):
        self.xp_per_level = xp_per_level
        self.level = level


class LevelsHandler:
    __slots__ = ('obj',)

    _ATTRIBUTE_CATEGORY = "levels"
    _XP_FOR_LEVELS = (
        _NextLevelXp(level=0, xp_per_level=100),
        _NextLevelXp(level=5, xp_per_level=200),
        _NextLevelXp(level=10, xp_per_level=300),
        _NextLevelXp(level=15, xp_per_level=500),
        _NextLevelXp(level=25, xp_per_level=1000),
        _NextLevelXp(level=50, xp_per_level=5000),
        _NextLevelXp(level=75, xp_per_level=10000),
        _NextLevelXp(level=100, xp_per_level=100000),
    )

    _LEVELS_FOR_STATS = {
        "primary": 4,
        "secondary": 5,
        "tertiary": 6,
    }

    def __init__(self, obj: 'BaseCharacter'):
        self.obj = obj
        if self.xp is None:
            self.xp = 0

        if self.level is None:
            self.level = 1

    @property
    def xp(self) -> int:
        return self.obj.attributes.get("xp", category=self._ATTRIBUTE_CATEGORY)

    @xp.setter
    def xp(self, value: int):
        self.obj.attributes.add("xp", category=self._ATTRIBUTE_CATEGORY, value=value)

    @property
    def level(self) -> int:
        return self.obj.attributes.get("level", category=self._ATTRIBUTE_CATEGORY)

    @level.setter
    def level(self, value: int):
        self.obj.attributes.add("level", category=self._ATTRIBUTE_CATEGORY, value=value)

    def get_xp_for_next_level(self) -> int:
        """
        Returns the required xp for the next level.
        """
        current_level = self.level
        xp_per_level = self._XP_FOR_LEVELS[0]
        for next_level_xp in self._XP_FOR_LEVELS:
            if current_level < next_level_xp.level:
                xp_per_level = next_level_xp.xp_per_level
            else:
                break

        return xp_per_level

    def add_xp(self, xp):
        """
        Add new XP.

        Args:
            xp (int): The amount of gained XP.
        """
        new_xp = self.xp + xp
        if new_xp > self.get_xp_for_next_level():
            self.xp = 0
            self.at_level_up()
        else:
            self.xp = new_xp

    def at_level_up(self):
        new_level = self.level + 1
        self.level = new_level

        # By default, we use the lowest values, useful when generating mobs
        stats = {
            "strength": "tertiary",
            "cunning": "tertiary",
            "will": "tertiary"
        }
        min_hp, max_hp = (1, 6)
        min_mana, max_mana = (1, 6)

        # Get the adjustments based on the character class
        if cclass := self.obj.cclass:
            min_hp, max_hp = cclass.health_dice
            min_mana, max_mana = cclass.mana_dice
            stats[cclass.primary_stat] = "primary"
            stats[cclass.secondary_stat] = "secondary"

        is_pc = self.obj.is_pc
        if is_pc:
            # Players always get the maximum possible health and mana
            added_hp = max_hp
            added_mana = max_mana
        else:
            added_hp = random.randint(min_hp, max_hp)
            added_mana = random.randint(min_mana, max_mana)

        self.obj.hp_max += added_hp
        self.obj.mana_max += added_mana

        # We add the new health directly unless the character is dead or dying.
        if self.obj.hp > 0:
            self.obj.hp += added_hp

        self.obj.mana += added_mana

        # We increase the stat when a threshold is reached
        added_stats = set()
        for stat, stat_focus in stats.values():
            levels_for_stat = self._LEVELS_FOR_STATS[stat_focus]
            if new_level % levels_for_stat != 0:
                continue

            stat_value = getattr(self.obj, stat, 1)
            setattr(self.obj, stat, stat_value + 1)
            added_stats.add(stat)

        # Send the player a nice message.
        if is_pc:
            hp_gain_str = f"{added_hp} hp" if added_hp else ""
            mana_gain_str = f"{added_hp} mana" if added_mana else ""
            stat_gain_str = ",".join(f"1 {stat}" for stat in added_stats)
            msg = (
                f"|wYou level up!\n"
                f"You gain {hp_gain_str}{mana_gain_str}{stat_gain_str}!|n"
            )
            self.obj.msg(msg)

        # If the object has a hook for additional level up effects, it is called here.
        if obj_hook := getattr(self.obj, "at_level_up", None):
            obj_hook()
