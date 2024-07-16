"""
EvAdventure character generation.

"""
import random

from django.conf import settings

from evennia import logger
from evennia.contrib.grid.xyzgrid.xyzgrid import get_xyzgrid
from evennia.objects.models import ObjectDB
from evennia.prototypes.spawner import spawn
from evennia.utils.evmenu import EvMenu
from typeclasses.characters import Character
from world.characters.classes import CharacterClasses, CharacterClass
from world.characters.races import Races, Race
from .random_tables import chargen_tables
from .rules import dice

_ABILITIES = {
    "STR": "strength",
    "WIL": "will",
    "CUN": "cunning",
}

_TEMP_SHEET = """
{name} the {race} {cclass}

STR +{strength}
CUN +{cunning}
WIL +{will}

{description}

Your belongings:
{equipment}
"""

_SORTED_RACES = sorted(list(Races.values()), key=lambda race: race.name)
_SORTED_CLASSES = sorted(list(CharacterClasses.values()), key=lambda cclass: cclass.name)


class TemporaryCharacterSheet:
    """
    This collects all the rules for generating a new character. An instance of this class is used
    to pass around the current character state during character generation and also applied to
    the character at the end. This class instance can also be saved on the menu to make sure a user
    is not losing their half-created character.
    """

    def _initial_stats_for_class(self, cclass: CharacterClass) -> dict[str, int]:
        stats = {"strength": 1, "cunning": 1, "will": 1}
        stats[cclass.primary_stat] = 3
        stats[cclass.secondary_stat] = 2
        return stats

    def _random_class(self) -> CharacterClass:
        return random.choice(_SORTED_CLASSES)

    def _random_race(self) -> Race:
        return random.choice(_SORTED_RACES)

    def swap_race(self, new_race: Race):
        # Remove previous modifiers
        self.strength -= self.race.strength_mod
        self.will -= self.race.will_mod
        self.cunning -= self.race.cunning_mod

        self.race = new_race

        # Apply new modifiers
        # TODO This should be a trait modifier instead
        self.strength += self.race.strength_mod
        self.will += self.race.will_mod
        self.cunning += self.race.cunning_mod

    def __init__(self):
        # name will likely be modified later
        self.name = dice.roll_random_table("1d282", chargen_tables["name"])

        self.race = self._random_race()
        self.cclass = self._random_class()

        _stats = self._initial_stats_for_class(self.cclass)
        self.strength = _stats["strength"]
        self.will = _stats["will"]
        self.cunning = _stats["cunning"]

        self.strength += self.race.strength_mod
        self.will += self.race.will_mod
        self.cunning += self.race.cunning_mod

        # physical attributes (only for rp purposes)
        physique = dice.roll_random_table("1d20", chargen_tables["physique"])
        face = dice.roll_random_table("1d20", chargen_tables["face"])
        skin = dice.roll_random_table("1d20", chargen_tables["skin"])
        hair = dice.roll_random_table("1d20", chargen_tables["hair"])
        clothing = dice.roll_random_table("1d20", chargen_tables["clothing"])
        speech = dice.roll_random_table("1d20", chargen_tables["speech"])
        virtue = dice.roll_random_table("1d20", chargen_tables["virtue"])
        vice = dice.roll_random_table("1d20", chargen_tables["vice"])
        background = dice.roll_random_table("1d20", chargen_tables["background"])
        misfortune = dice.roll_random_table("1d20", chargen_tables["misfortune"])
        alignment = dice.roll_random_table("1d20", chargen_tables["alignment"])

        self.desc = (
            f"You are {physique} with a {face} face, {skin} skin, {hair} hair, {speech} speech, and"
            f" {clothing} clothing. You were a {background.title()}, but you were {misfortune} and"
            f" ended up a wanderer. You are {virtue} but also {vice}. You tend towards {alignment}."
        )

        self.hp_max = 10 + self.cclass.health_dice[1]
        self.hp = self.hp_max
        self.mana_max = 10 + self.cclass.mana_dice[1]
        self.mana = self.mana_max
        self.stamina_max = 10 + self.cclass.stamina_dice[1]
        self.stamina = self.stamina_max

        # random equipment
        self.armor = dice.roll_random_table("1d20", chargen_tables["armor"])

        _helmet_and_shield = dice.roll_random_table("1d20", chargen_tables["helmets and shields"])
        self.helmet = "helmet" if "helmet" in _helmet_and_shield else "none"
        self.shield = "shield" if "shield" in _helmet_and_shield else "none"

        self.weapon = dice.roll_random_table("1d20", chargen_tables["starting weapon"])

        self.backpack = [
            "ration",
            "ration",
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 1"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 2"]),
        ]

    def show_sheet(self):
        """
        Show a temp character sheet, a compressed version of the real thing.

        """
        equipment = (self.armor, self.helmet, self.shield, self.weapon, self.backpack)

        return _TEMP_SHEET.format(
            name=self.name,
            strength=self.strength,
            cunning=self.cunning,
            will=self.will,
            race=self.race,
            cclass=self.cclass,
            description=self.desc,
            equipment=", ".join((str(eq) for eq in equipment)),
        )

    def apply(self, account):
        """
        Once the chargen is complete, call this create and set up the character.

        """
        grid = get_xyzgrid()
        start_location = grid.get_room(('12', '7', 'riverport'))
        if start_location:
            start_location = start_location[0] # The room we got above is a queryset so we get it by index
        else:
            start_location = ObjectDB.objects.get_id(settings.START_LOCATION)

        default_home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
        permissions = settings.PERMISSION_ACCOUNT_DEFAULT

        # creating character with given abilities
        new_character, _err = Character.create(
            key=self.name,
            location=start_location,
            home=default_home,
            permissions=permissions,
            attributes=(
                ("strength", self.strength),
                ("cunning", self.cunning),
                ("will", self.will),
                ("race_key", self.race.key),
                ("cclass_key", self.cclass.key),
                ("hp", self.hp),
                ("hp_max", self.hp_max),
                ("mana", self.hp),
                ("mana_max", self.hp_max),
                ("stamina", self.stamina),
                ("stamina_max", self.stamina_max),
                ("desc", self.desc),
            ),
        )

        new_character.locks.add(
            "puppet:id(%i) or pid(%i) or perm(Developer) or pperm(Developer);delete:id(%i) or"
            " perm(Admin)" % (new_character.id, account.id, account.id)
        )
        # spawn equipment
        # TODO: add item prototypes
        # none of the equipment from the random tables have prototypes, so there is no starting gear
        if self.weapon:
            try:
                weapon = spawn(self.weapon)
                new_character.equipment.move(weapon[0])
            except KeyError:
                logger.log_err(f"[Chargen] Could not spawn Weapon: Prototype not found for '{self.weapon}'.")

        if self.armor:
            try:
                armor = spawn(self.armor)
                new_character.equipment.move(armor[0])
            except KeyError:
                logger.log_err(f"[Chargen] Could not spawn Armor: Prototype not found for '{self.armor}'.")

        if self.shield:
            try:
                shield = spawn(self.shield)
                new_character.equipment.move(shield[0])
            except KeyError:
                logger.log_err(f"[Chargen] Could not spawn Shield: Prototype not found for '{self.shield}'.")

        if self.helmet:
            try:
                helmet = spawn(self.helmet)
                new_character.equipment.move(helmet[0])
            except KeyError:
                logger.log_err(f"[Chargen] Could not spawn Helmet: Prototype not found for '{self.helmet}'.")

        for item in self.backpack:
            try:
                item = spawn(item)
                new_character.equipment.move(item[0])
            except KeyError:
                logger.log_err(f"[Chargen] Could not spawn Item: Prototype not found for '{item}'.")

        return new_character


# chargen menu
def node_chargen(caller, raw_string, **kwargs):
    """
    This node is the central point of chargen. We return here to see our current
    sheet and break off to edit different parts of it.
    """
    tmp_character = kwargs["tmp_character"]
    options = [
        {"desc": "Change your name", "goto": ("node_change_name", kwargs)},
        {"desc": "Change your race", "goto": ("node_show_races", kwargs)},
        {"desc": "Change your class", "goto": ("node_show_classes", kwargs)},
        {"desc": "Accept and create character", "goto": ("node_apply_character", kwargs)},
    ]
    text = tmp_character.show_sheet()

    return text, options


def _update_name(caller, raw_string, **kwargs):
    """
    Used by node_change_name below to check what user entered and update the name if appropriate.

    """
    if raw_string:
        tmp_character = kwargs["tmp_character"]
        tmp_character.name = raw_string.lower().capitalize()

    return "node_chargen", kwargs


def node_change_name(caller, raw_string, **kwargs):
    """
    Change the random name of the character.

    """
    tmp_character = kwargs["tmp_character"]

    text = (
        f"Your current name is |w{tmp_character.name}|n. Enter a new name or leave empty to abort."
    )
    options = {"key": "_default", "goto": (_update_name, kwargs)}

    return text, options


def node_apply_character(caller, raw_string, **kwargs):
    """
    End chargen and create the character. We will also puppet it.

    """
    tmp_character = kwargs["tmp_character"]
    new_character = tmp_character.apply(caller)
    caller.db._playable_characters.append(new_character)
    session = caller.ndb._evmenu._session
    caller.puppet_object(session=session, obj=new_character)

    text = "Character created!"

    return text, None


def start_chargen(caller, session=None):
    """
    This is a start point for spinning up the chargen from a command later.
    """
    menu_tree = {
        "node_chargen": node_chargen,
        "node_change_name": node_change_name,
        "node_apply_character": node_apply_character,
        "node_show_classes": node_show_classes,
        "node_select_class": node_select_class,
        "node_apply_class": node_apply_class,
        "node_show_races": node_show_races,
        "node_select_race": node_select_race,
        "node_apply_race": node_apply_race,

    }

    # this generates all random components of the character
    tmp_character = TemporaryCharacterSheet()

    EvMenu(
        caller,
        menu_tree,
        startnode="node_chargen",
        session=session,
        startnode_input=("sgsg", {"tmp_character": tmp_character}),
    )


def node_show_classes(caller, raw_string, **kwargs):
    """Starting page and Class listing."""
    text = """\
        Select a |cClass|n.

        Select one by number below to view its details, or |whelp|n
        at any time for more info.
    """

    options = [
        {
            "desc": "|c{}|n".format(cclass.name),
            "goto": ("node_select_class", {"cclass": cclass, **kwargs}),
        }
        for cclass in _SORTED_CLASSES
    ]

    return (text, "Type in the number next to the class to have more info."), options


def node_select_class(caller, raw_string, **kwargs):
    """Class detail and selection menu node."""
    try:
        choice = int(raw_string.strip())
        cclass = _SORTED_CLASSES[choice - 1]
    except (ValueError, KeyError, IndexError):
        caller.msg("|rInvalid choice. Try again.")
        return None

    text = cclass.desc + "\nWould you like to become this class?"
    help = "Examine the properties of this class and decide whether\n"
    help += "to use its starting attributes for your character."
    options = (
        {
            "key": ("Yes", "ye", "y"),
            "desc": f"Become {cclass.name}",
            "goto": ("node_apply_class", {"cclass": cclass, **kwargs}),
        },
        {
            "key": ("No", "n", "_default"),
            "desc": "Return to Class selection",
            "goto": "node_show_classes"
        }
    )
    return (text, help), options


def node_apply_class(caller, raw_string, **kwargs):
    cclass = kwargs.get('cclass')
    tmp_character = kwargs["tmp_character"]
    tmp_character.cclass = cclass

    return node_chargen(caller, '', tmp_character=tmp_character)


def node_show_races(caller, raw_string, **kwargs):
    """Starting page and Class listing."""
    text = """\
        Select a |cRace|n.

        Select one by number below to view its details, or |whelp|n
        at any time for more info.
    """

    options = [
        {
            "desc": "|c{}|n".format(race.name),
            "goto": ("node_select_race", {"race": race, **kwargs}),
        }
        for race in _SORTED_RACES
    ]

    return (text, "Select a race to show its details"), options


def node_select_race(caller, raw_string, **kwargs):
    """Race detail and selection menu node."""
    try:
        choice = int(raw_string.strip())
        race = _SORTED_RACES[choice - 1]
    except (ValueError, KeyError, IndexError):
        caller.msg("|rInvalid choice. Try again.")
        return None

    text = race.desc + "\nWould you like to become this race?"
    help = "Examine the properties of this race and decide whether\n"
    help += "to use its starting attributes for your character."
    options = (
        {
            "key": ("Yes", "ye", "y"),
            "desc": f"Become {race.name}",
            "goto": ("node_apply_race", {'race': race, **kwargs}),
        },
        {
            "key": ("No", "n", "_default"),
            "desc": "Return to Class selection",
            "goto": "node_show_races"
        }
    )

    return (text, help), options


def node_apply_race(caller, raw_string, **kwargs):
    race = kwargs.get('race')
    tmp_character = kwargs["tmp_character"]
    tmp_character.swap_race(race)
    caller.msg('Swapped race!')

    return node_chargen(caller, '', tmp_character=tmp_character)
