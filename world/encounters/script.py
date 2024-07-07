from typing import Self

from evennia.typeclasses.attributes import AttributeProperty
from typeclasses.scripts import Script
from world.encounters.data import ENCOUNTERS


class EncounterScript(Script):
    ENCOUNTER_MAX = 49  # The overworld map is about 5280 tiles, 49 gives us a grid of 7 by 7
    REPOP_DELAY = 43200  # A day is 86400 seconds divided by 2 for the default game time 2x speed
    REPOP_MAX = 12  # This will make our encounters take a few days to max out

    encounter_data = AttributeProperty()

    @classmethod
    def get(cls) -> Self:
        return EncounterScript.objects.get_or_create(db_key="encounter_script")[0]

    def at_script_creation(self):
        self.key = "encounter_script"
        self.interval = self.REPOP_DELAY
        self.persistent = True

    def at_repeat(self, **kwargs):
        encounter_data = self.encounter_data
        if encounter_data is None:
            self.encounter_data = {}

        amount_encounters = len(self.encounter_data)
        if amount_encounters < self.ENCOUNTER_MAX:
            amount_needed = min(self.ENCOUNTER_MAX - amount_encounters, self.REPOP_MAX)
            self.add_encounters(amount_needed)

    def add_encounters(self, amount):
        encounter_grid = [[None for _ in range(7)] for _ in range(7)]
        for grid_tuple, encounter in self.encounter_data.items():
            grid_x, grid_y = grid_tuple
            encounter_grid[grid_y][grid_x] = encounter

        for y, row in enumerate(encounter_grid):
            for x, encounter in enumerate(row):
                if encounter:
                    continue

                encounter = self.add_encounter(x, y)
                encounter_grid[y][x] = encounter
                self.encounter_data[(x, y)] = encounter
                amount -= 1
                if amount <= 0:
                    return

    def add_encounter(self, grid_x, grid_y) -> dict:
        near_border = grid_x <= 1 or grid_x >= 6 or grid_y <= 1 or grid_y >= 6
        near_center = abs(3 - grid_x) <= 2 or abs(3 - grid_y) <= 2
        if near_border:
            encounter_level = 3
        elif near_center:
            encounter_level = 1
        else:
            encounter_level = 2

        return {"encounter_level": encounter_level}

    def get_encounter_at(self, location, map_x, map_y):
        encounter_data = self.encounter_data
        if not encounter_data:
            return

        chosen_tuple = None
        chosen_encounter = None
        for grid_tuple, encounter in self.encounter_data.items():
            grid_x, grid_y = grid_tuple
            left = grid_x * 100
            right = left + 100
            top = grid_y * 100
            bottom = grid_y + 100
            if left < map_x < right and top < map_y < bottom:
                chosen_encounter = encounter
                chosen_tuple = grid_tuple
                break

        if chosen_tuple:
            players = [char for char in location.contents_get(content_type="character") if char.is_pc]
            self.encounter_data.pop(chosen_tuple)
            for encounter_type in ENCOUNTERS.values():
                if chosen_encounter["encounter_level"] >= encounter_type.encounter_level:
                    mobs = encounter_type.spawn(location, players=players)
                    return mobs
