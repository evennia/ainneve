"""
Utility objects.
"""
from evennia import TICKER_HANDLER as tickerhandler
from world import archetypes, races, skills


def sample_char(char, archetype, race, focus=None):
    """Loads sample traits onto a character.

    Args:
        char (Character): character to load traits
        archetype (str): name of base archetype
        race (str): name of race to become
        focus Optional(str): focus to apply. if None, default is race's
            first item in foci collection
        """
    archetypes.apply_archetype(char, archetype, reset=True)
    char.traits.STR.base += 1
    char.traits.PER.base += 1
    char.traits.INT.base += 1
    char.traits.DEX.base += 1
    char.traits.CHA.base += 1
    char.traits.VIT.base += 2
    char.traits.MAG.base += 2
    focus = focus or races.load_race(race).foci[0]
    races.apply_race(char, race, focus)
    archetypes.calculate_secondary_traits(char.traits)
    archetypes.finalize_traits(char.traits)
    tickerhandler.add(char, 6, hook_key='at_turn_start')
    skills.apply_skills(char)
    skills.finalize_skills(char.skills)
