from evennia.prototypes.spawner import spawn
from evennia.typeclasses.attributes import AttributeProperty
from typeclasses.characters import BaseCharacter


class BaseMob(BaseCharacter):
    starting_equipment_prototypes = AttributeProperty()
    mob_scaling = AttributeProperty()

    def at_object_creation(self):
        super().at_object_creation()
        self.hp = self.hp_max
        self.mana = self.mana_max
        if self.starting_equipment_prototypes:
            self._spawn_and_equip_starting_equipment()

    def _spawn_and_equip_starting_equipment(self):
        equipment = spawn(*self.starting_equipment_prototypes)
        for eq in equipment:
            self.equipment.move(eq)

    def scale_to_level(self, level: int):
        if level <= 1:
            return

        self.hp_max += int(self.hp_max * level * self.mob_scaling.get("hp", 0.1))
        self.mana_max += int(self.mana_max * level * self.mob_scaling.get("mana", 0.1))

        stat_levels = {
            "strength": 6,
            "cunning": 6,
            "will": 6,
        }
        if self.cclass:
            stat_levels[self.cclass.primary_stat] = 4
            stat_levels[self.cclass.secondary_stat] = 5

        for stat, value in stat_levels.items():
            stat_levels[stat] = int(level / value)

        self.strength += int(stat_levels["strength"] * self.mob_scaling.get("strength", 0.1))
        self.cunning += int(stat_levels["cunning"] * self.mob_scaling.get("cunning", 0.1))
        self.will += int(stat_levels["will"] * self.mob_scaling.get("will", 0.1))

        self.levels.level = level

    def at_death(self):
        """
        Called when this living thing dies.

        """
        self.location.msg_contents(f"$You() $conj(die).", from_obj=self)
        self.delete()
