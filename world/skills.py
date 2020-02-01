"""
Skills module.

This module contains data and functions related to character Skills.
Skills in OA are treated as a modifier to a standard roll that is
typically compared to a target number of 5, though that can vary for
some skills.

Its public module functions are to be used primarily during the character
creation process.

Classes:

    `Skill`: convenience object for skill display data

Module Functions:

    - `apply_skills(char)`

        Initializes a character's db.skills attribute to support skill
        traits. In OA, all skills start matching their base trait before
        the player allocates a number of +1 and -1 counters.

    - `load_skill(skill)`

        Loads an instance of the Skill class by name for display of
        skill name and description.

    - `validate_skills(char)`

        Validates a player's skill penalty and bonus token allocations.
        Because the requirements depend on the char's INT trait, it
        accepts the entire char as its argument.

    - `finalize_skills(skills)`

        Finalizes and "saves" the player's allocations and deletes the
        'plus' and 'minus' extra keys used during chargen.
"""
from math import ceil

class SkillException(Exception):
    def __init__(self, msg):
        self.msg = msg


# global skill data is minimal, and can just be stored in a dict for now
_SKILL_DATA = {
    # STR
    'escape': {
        'name': 'Escape',
        'base': 'STR',
        'desc': ("|mEscape|n represents a character's ability to free "
                 "themselves from restraints such as cuffs or shackles. It "
                 "also entails breaking free of prison or jail cells.")
    },
    'climb': {
        'name': 'Climb',
        'base': 'STR',
        'desc': ("|mClimb|n represents the proficiency in climbing difficult "
                 "slopes or sheer walls.")
    },
    'jump': {
        'name': 'Jump',
        'base': 'STR',
        'desc': ("|mJump|n is the ability to leap great distances such as "
                 "across pits or over obstacles. Encumbrance may affect jump "
                 "distance.")
    },
    # PER
    'lockpick': {
        'name': 'Lock Pick',
        'base': 'PER',
        'desc': ("|mLock Pick|n represents the proficiency in manipulating "
                 "pins and tumblers to open a lock without a key.")
    },
    'listen': {
        'name': 'Listen',
        'base': 'PER',
        'desc': ("|mListen|n is the ability to hear distant or quiet noises. "
                 "Characters may listen intently near closed doors or long "
                 "hallways for approaching enemies or other hushed "
                 "activities.")
    },
    'sense': {
        'name': 'Sense Danger',
        'base': 'PER',
        'desc': ("|mSense Danger|n is the ability to assess the level of "
                 "danger that enemies and situations possess.")
    },
    # INT
    'appraise': {
        'name': 'Appraise',
        'base': 'INT',
        'desc': ("|mAppraise|n is the ability to determine an accurate value "
                 "of an item's worth and abilities.")
    },
    'medicine': {
        'name': 'Medicine',
        'base': 'INT',
        'desc': ("|mMedicine|n is the practice of healing and nurturing. A "
                 "character who practices medicine can remove heal damage or "
                 "adverse conditions, or cure certain poisons. ")
    },
    'survival': {
        'name': 'Survival',
        'base': 'INT',
        'desc': ("|mSurvival|n is the ability to procure shelter, fire, food "
                 "and drink in an otherwise inhospitable or untamed location.")
    },
    # DEX
    'balance': {
        'name': 'Balance',
        'base': 'DEX',
        'desc': ("|mBalance|n is the ability to stay centered and not fall from "
                 "a narrow ledge or walkway. It is a character's ability to "
                 "keep their equilibrium even on unsteady terrain.")
    },
    'sneak': {
        'name': 'Sneak',
        'base': 'DEX',
        'desc': ("|mSneak|n is the skill of remaining unseen and unheard by "
                 "enemies while moving stealthily.")
    },
    'throwing': {
        'name': 'Throwing',
        'base': 'DEX',
        'desc': ("|mThrowing|n is the act of tossing an [Item], object or "
                 "weapon.")
    },
    # CHA
    'animal': {
        'name': 'Animal Handle',
        'base': 'CHA',
        'desc': ("|mAnimal Handle)|n is the innate feat of being able to calm "
                 "and communicate non-verbally with a creature of less-than "
                 "humanoid intelligence. The target number to succeed is equal "
                 "to 10 - intelligence of the animal.")
    },
    'barter': {
        'name': 'Barter',
        'base': 'CHA',
        'desc': ("|mBarter|n is the the timeless art of negotiation in an "
                 "effort to lower the price on an item for sale. This ability "
                 "can only be done once per merchant per day.")
    },
    'leadership': {
        'name': 'Leadership',
        'base': 'CHA',
        'desc': ("|mLeadership|n is the natural ability to raise the spirits "
                 "and morale of those around you. It also enhances grouping.")
    },
}

# skill groupings used in skills command
ALL_SKILLS = ('escape', 'climb', 'jump',
              'lockpick', 'listen', 'sense',
              'appraise', 'medicine', 'survival',
              'balance', 'sneak', 'throwing',
              'animal', 'barter', 'leadership')
STR_SKILLS = [s for s in ALL_SKILLS if _SKILL_DATA[s]['base'] == 'STR']
PER_SKILLS = [s for s in ALL_SKILLS if _SKILL_DATA[s]['base'] == 'PER']
INT_SKILLS = [s for s in ALL_SKILLS if _SKILL_DATA[s]['base'] == 'INT']
DEX_SKILLS = [s for s in ALL_SKILLS if _SKILL_DATA[s]['base'] == 'DEX']
CHA_SKILLS = [s for s in ALL_SKILLS if _SKILL_DATA[s]['base'] == 'CHA']

def apply_skills(char):
    """Sets up a character's initial skill traits.

    Args:
        char (Character): the character being initialized
    """
    char.skills.clear()
    for skill, data in _SKILL_DATA.items():
        char.skills.add(
            key=skill,
            type='static',
            base=char.traits[data['base']].actual,
            mod=0,
            name=data['name'],
            extra=dict(plus=0, minus=0)
        )


def load_skill(skill):
    """Retrieves an instance of a `Skill` class.

    Args:
        skill (str): case insensitive skill name

    Returns:
        (Skill): instance of the named Skill
    """
    skill = skill.lower()
    if skill in ALL_SKILLS:
        return Skill(**_SKILL_DATA[skill])
    else:
        raise SkillException('Invalid skill name.')


def validate_skills(char):
    """Validates a player's skill allocations during chargen.

    Args:
        char (Character): character with populated skills TraitHandler

    Returns:
        (tuple[bool, str]): first value is whether the skills are valid,
            second value is error message
    """
    minus_count = 3
    plus_count = ceil(char.traits.INT.actual / 3.0)
    if sum(char.skills[s].minus for s in ALL_SKILLS) != minus_count:
        return False, 'Not enough -1 counters allocated.'
    if sum(char.skills[s].plus for s in ALL_SKILLS) != plus_count:
        return False, 'Not enough +1 counters allocated.'
    return True, ''


def finalize_skills(skills):
    """Sets/calculates the permanent skill values at the end of chargen.

    Args:
        skills (TraitHandler): validated skills TraitHandler collection

    Note:
        During chargen, penalty counters are applied to the `base`
        property, and bonus counters to the `mod`. This function is
        called after validation to set the combined values as `base`
        and reset `mod` to zero for game play.
    """
    for skill in ALL_SKILLS:
        skills[skill].base += skills[skill].plus
        skills[skill].base -= skills[skill].minus
        del skills[skill].plus
        del skills[skill].minus


class Skill(object):
    """Represents a Skill's display attributes for use in chargen.

    Args:
        name (str): display name for skill
        desc (str): description of skill
    """
    def __init__(self, name, desc, base):
        self.name = name
        self.desc = desc
        self.base = base

