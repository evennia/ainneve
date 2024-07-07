import random

from evennia.prototypes.spawner import spawn

ENCOUNTERS = {}


class EncounterEntry:
    __slots__ = ('prototype', 'amount', 'chance', 'scale_amount')

    def __init__(
            self, prototype: str,
            amount: tuple[int, int] = (1, 1),
            chance: int = 100,
            scale_amount: int = 1
    ):
        self.prototype = prototype
        self.amount = amount
        self.chance = chance
        self.scale_amount = scale_amount

    def spawn(self):
        return spawn(self.prototype)[0]


class EncounterType:
    __slots__ = ("key", "name", "encounter_level", "entries")

    def __init__(self, key: str, name: str, encounter_level: int, entries: tuple[EncounterEntry, ...]):
        self.key = key
        self.name = name
        self.encounter_level = encounter_level
        self.entries = entries
        ENCOUNTERS[key] = self

    def spawn(self, location, players):
        player_count = len(players)
        highest_level = max((player.levels.level for player in players))

        group = []
        for entry in self.entries:
            if entry.chance < 100 and random.randint(1, 100) > entry.chance:
                continue

            amount = random.randint(*entry.amount) + int(entry.scale_amount * player_count)
            for _ in range(amount):
                mob = entry.spawn()
                mob.scale_to_level(highest_level)
                mob.location = location
                group.append(mob)

        location.msg_contents(f"You run into {self.name}!")

        return group


ENCOUNTER_GOBLIN_SCOUTS = EncounterType(
    "goblin_scouts", "goblin scouts", 1,
    (
        EncounterEntry("mob_goblin_weak", amount=(1, 4)),
        EncounterEntry("mob_goblin_common", amount=(1, 2), chance=30),
    )
)

ENCOUNTER_GOBLIN_WARRIORS = EncounterType(
    "goblin_warriors", "a group of goblin warriors", 2,
    (
        EncounterEntry("mob_goblin_weak", amount=(1, 2), chance=30),
        EncounterEntry("mob_goblin_common", amount=(1, 2), chance=30),
        EncounterEntry("mob_goblin_warrior", amount=(1, 2), chance=100),
    )
)

ENCOUNTER_GOBLIN_PACK = EncounterType(
    "goblin_pack", "a pack of goblins", 3,
    (
        EncounterEntry("mob_goblin_weak", amount=(1, 4)),
        EncounterEntry("mob_goblin_common", amount=(1, 4)),
        EncounterEntry("mob_goblin_warrior", amount=(2, 4)),
        EncounterEntry("mob_goblin_warchief", amount=(1, 1), scale_amount=0),
    )
)