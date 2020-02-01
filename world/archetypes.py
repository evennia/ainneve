"""
Ainneve archetypes module.

This module encapsulates archetype-related data including character
trait definitions, and eventually default ability stats and OA talents to
select from when leveling up.

Archetype classes are meant to be loaded by name as needed to provide access
to archetype-specific data, not to be saved on a `Character` object. Only
the archetype name is stored in the character's `db` attribute handler,
and that value is generally set by the `apply_archetype` module function.

Module Functions:

    - `apply_archetype(char, name, reset=False)`

        Causes character `char` to become archetype `name`. Initializes db
        attributes on `char` to archetype defaults. Can be called twice on
        the same character with two different `name` parameters to create
        a dual archetype. May also be called with reset=True to remove
        any existing archetype and initialize the character with only the
        named one.

    - `get_remaining_allocation(traits)`

        Returns the nummber of trait points left for the player to allocate
        to primary traits.

    - `validate_primary_traits(traits)`

        Confirms that all primary traits total 30 points, and all but MAG
        are at least 1 and no greater than 10.

    - `calculate_secondary_traits(traits)`

        Called to set initial base values for secondary traits and save
        rolls.

    - `finalize_traits(traits)`

        Called at the end of chargen to apply modifiers to base values and
        reset `mod` values for normal game play.

    - `load_archetype(name)`

        Returns an instance of the named Archetype class.
"""

from world.rulebook import roll_max
from evennia.utils import fill
from evennia.utils.evtable import EvTable


class ArchetypeException(Exception):
    def __init__(self, msg):
        self.msg = msg

BASE_ARCHETYPES = ('Arcanist', 'Scout', 'Warrior')
DUAL_ARCHETYPES = ('Warrior-Scout', 'Warrior-Arcanist', 'Arcanist-Scout')
VALID_ARCHETYPES = BASE_ARCHETYPES + DUAL_ARCHETYPES

PRIMARY_TRAITS = ('STR', 'PER', 'INT', 'DEX', 'CHA', 'VIT', 'MAG')
SECONDARY_TRAITS = ('HP', 'SP', 'BM', 'WM')
SAVE_ROLLS = ('FORT', 'REFL', 'WILL')
COMBAT_TRAITS = ('ATKM', 'ATKR', 'ATKU', 'DEF', 'PP')
OTHER_TRAITS = ('LV', 'XP', 'ENC', 'MV', 'ACT')

ALL_TRAITS = (PRIMARY_TRAITS + SECONDARY_TRAITS +
              SAVE_ROLLS + COMBAT_TRAITS + OTHER_TRAITS)

TOTAL_PRIMARY_POINTS = 30

def apply_archetype(char, name, reset=False):
    """Set a character's archetype and initialize traits.

    Used during character creation; initializes the traits collection. It
    can be called twice to make the character a Dual-Archetype.

    Args:
        char (Character): the character being initialized.
        name (str): single archetype name to apply. If the character already
            has a single archetype, it is combined with the existing as a
            dual archetype.
        reset (bool): if True, remove any current archetype and apply the
            named archetype as new.
    """
    name = name.title()
    if name not in VALID_ARCHETYPES:
        raise ArchetypeException('Invalid archetype.')

    if char.db.archetype is not None:
        if not reset:
            if char.db.archetype == name:
                raise ArchetypeException('Character is already a {}'.format(name))

            name = '-'.join((char.db.archetype, name))
            reset = True

    archetype = load_archetype(name)
    char.db.archetype = archetype.name
    if reset:
        char.traits.clear()
    for key, kwargs in archetype.traits.items():
        char.traits.add(key, **kwargs)


def get_remaining_allocation(traits):
    """Returns the number of trait points remaining to be assigned.

    Args:
        traits (TraitHandler): Partially loaded TraitHandler

    Returns:
        (int): number of trait points left for the player to allocate
    """
    allocated = sum(traits[t].actual for t in PRIMARY_TRAITS)
    return TOTAL_PRIMARY_POINTS - allocated


def validate_primary_traits(traits):
    """Validates proposed primary trait allocations during chargen.

    Args:
        traits (TraitHandler): TraitHandler loaded with proposed final
            primary traits

    Returns:
        (tuple[bool, str]): first value is whether the traits are valid,
            second value is error message
    """
    total = sum(traits[t].actual for t in PRIMARY_TRAITS)
    if total > TOTAL_PRIMARY_POINTS:
        return False, 'Too many trait points allocated.'
    if total < TOTAL_PRIMARY_POINTS:
        return False, 'Not enough trait points allocated.'
    else:
        return True, None


def calculate_secondary_traits(traits):
    """Calculates secondary traits

    Args:
        traits (TraitHandler): factory attribute with primary traits
        populated.
    """
    # secondary traits
    traits.HP.base = traits.VIT.actual
    traits.SP.base = traits.VIT.actual
    # save rolls
    traits.FORT.base = traits.VIT.actual
    traits.REFL.base = traits.DEX.actual
    traits.WILL.base = traits.INT.actual
    # combat
    traits.ATKM.base = traits.STR.actual
    traits.ATKR.base = traits.PER.actual
    traits.ATKU.base = traits.DEX.actual
    traits.DEF.base = traits.DEX.actual
    # mana
    traits.BM.max = 10 if traits.MAG.actual > 0 else 0
    traits.WM.max = 10 if traits.MAG.actual > 0 else 0
    # misc
    traits.STR.carry_factor = 10
    traits.STR.lift_factor = 20
    traits.STR.push_factor = 40
    traits.ENC.max = traits.STR.lift_factor * traits.STR.actual


def finalize_traits(traits):
    """Applies all pending modifications to starting traits.

    During the chargen process, race-based bonuses and player
    allocations are applied to trait modifiers. This function
    applies any `mod` values to the traits' `base`, then resets
    the `mod` property.
    """
    for t in PRIMARY_TRAITS + SECONDARY_TRAITS + SAVE_ROLLS:
        traits[t].base = traits[t].actual if traits[t].actual <= 10 else 10
        traits[t].reset_mod()

    if traits.BM.base == 0:
        traits.BM.max = 0
    if traits.WM.base == 0:
        traits.WM.max = 0


def load_archetype(name):
    """Loads an instance of the named Archetype class.

    Args:
        name (str): Name of either single or dual-archetype

    Return:
        (Archetype): An instance of the requested archetype class.
    """
    name = name.title()
    if '-' in name:  # dual arch
        archetype = _make_dual(*[load_archetype(n) for
                                 n in name.split('-', 1)])
    else:
        try:
            archetype = globals().get(name, None)()
        except TypeError:
            raise ArchetypeException("Invalid archetype specified.")
    return archetype

def _make_dual(a, b):
    """Creates a dual archetype class out of two basic `Archetype` classes.

    Args:
        a (Archetype): first component Archetype
        b (Archetype): second component Archetype

    Returns:
        (Archetype): dual Archetype class
    """
    if '-' in a.name or '-' in b.name:
        raise ArchetypeException('Cannot create Triple-Archetype')
    if a.name == b.name:
        raise ArchetypeException('Cannot create dual of the same Archetype')

    names = {
        frozenset(['Warrior', 'Scout']): 'Warrior-Scout',
        frozenset(['Warrior', 'Arcanist']): 'Warrior-Arcanist',
        frozenset(['Scout', 'Arcanist']): 'Arcanist-Scout'
    }
    dual = Archetype()
    for key, trait in dual.traits.items():
        trait['base'] = (a.traits.get(key, trait)['base'] +
                         b.traits.get(key, trait)['base']) // 2
        trait['mod'] = (a.traits.get(key, trait)['mod'] +
                        b.traits.get(key, trait)['mod']) // 2
    dual.health_roll = min(a.health_roll, b.health_roll, key=roll_max)
    dual.name = names[frozenset([a.name, b.name])]
    desc = "|c{}s|n have a blend of the qualities of both component archetypes.\n\n"
    desc += a._desc + '\n\n' + b._desc
    dual.desc = desc.format(dual.name)
    dual.__class__.__name__ = dual.name.replace('-', '')
    return dual


# Archetype Classes


class Archetype(object):
    """Base archetype class containing default values for all traits."""
    def __init__(self):
        self.name = None
        self._desc = None

        # base traits data
        self.traits = {
            # primary
            'STR': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Strength'},
            'PER': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Perception'},
            'INT': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Intelligence'},
            'DEX': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Dexterity'},
            'CHA': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Charisma'},
            'VIT': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Vitality'},
            # magic
            'MAG': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Magic'},
            'BM': {'type': 'gauge', 'base': 0, 'mod': 0, 'min': 0, 'max': 10, 'name': 'Black Mana'},
            'WM': {'type': 'gauge', 'base': 0, 'mod': 0, 'min': 0, 'max': 10, 'name': 'White Mana'},
            # secondary
            'HP': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Health'},
            'SP': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Stamina'},
            # saves
            'FORT': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Fortitude Save'},
            'REFL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Reflex Save'},
            'WILL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Will Save'},
            # combat
            'ATKM': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Melee Attack'},
            'ATKR': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Ranged Attack'},
            'ATKU': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Unarmed Attack'},
            'DEF': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Defense'},
            'ACT': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Action Points'},
            'PP': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Power Points'},
            # misc
            'ENC': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Carry Weight'},
            'MV': {'type': 'gauge', 'base': 6, 'mod': 0, 'min': 0, 'name': 'Movement Points'},
            'LV': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Level'},
            'XP': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Experience',
                   'extra': {'level_boundaries': (500, 2000, 4500, 'unlimited')}},
        }
        self.health_roll = None

    @property
    def ldesc(self):
        """Returns a formatted description of the Archetype."""
        desc = "Archetype: |c{archetype}|n\n"
        desc += '~' * (11 + len(self.name)) + '\n'
        desc += self.desc
        desc += '\n\n'
        desc += "|c{archetype}s|n start with the following base primary traits:"
        desc += "\n{traits}\n"
        desc += "  Base |CMovement Points|n:    |w{mv:>2d}|n\n"
        desc += "  |CStamina|n Modifier:        |w{sp_mod:+>2d}|n\n"
        desc += "  |CPower Points|n Modifier:   |w{pp_mod:+>2d}|n\n"
        desc += "  |CReflex Save|n Modifier:    |w{refl_mod:+>2d}|n\n"
        desc += ("  When leveling up, |c{archetype}s|n gain "
                 "|w{health_roll}|C HP|n.\n")

        data = []
        for i in list(range(3)):
            data.append([self._format_trait_3col(self.traits[t])
                         for t in PRIMARY_TRAITS[i::3]])
        traits = EvTable(header=False, table=data)

        return desc.format(archetype=self.name,
                           traits=traits,
                           health_roll=self.health_roll,
                           mv=self.traits['MV']['base'],
                           sp_mod=self.traits['SP']['mod'],
                           pp_mod=self.traits['PP']['base'],
                           refl_mod=self.traits['REFL']['mod'])

    @property
    def desc(self):
        """The narrative description of the Archetype."""
        return self._desc

    @desc.setter
    def desc(self, desc):
        self._desc = desc

    def _format_trait_3col(self, trait):
        """Return a trait : value pair formatted for 3col layout"""
        return "|C{:<16.16}|n : |w{:>3}|n".format(
                    trait['name'], trait['base'])


class Arcanist(Archetype):
    """Represents the Arcanist archetype."""
    def __init__(self):
        super(Arcanist, self).__init__()
        self.name = 'Arcanist'
        self.desc = fill(
            "|cArcanists|n harness mysterious, arcane powers they pull from "
            "the ether. These magic and paranormal wielders employ occult "
            "powers that only they truly understand."
        )

        # set starting trait values
        self.traits['PER']['base'] = 4
        self.traits['INT']['base'] = 6
        self.traits['CHA']['base'] = 4
        self.traits['MAG']['base'] = 6
        self.traits['SP']['mod'] = -2
        self.traits['MV']['base'] = 7

        self.health_roll = '1d6-1'


class Scout(Archetype):
    """Represents the Scout archetype."""
    def __init__(self):
        super(Scout, self).__init__()
        self.name = 'Scout'
        self.desc = fill(
            "|cScouts|n are highly intelligent and well-trained individuals "
            "who prefer to work their secret craft in the shadows where "
            "they remain unseen. Scouts go by many names such as thieves, "
            "rogues and rangers but little is known by general society of "
            "their closely guarded secrets. "
        )

        # set starting trait values
        self.traits['STR']['base'] = 4
        self.traits['PER']['base'] = 6
        self.traits['INT']['base'] = 6
        self.traits['DEX']['base'] = 4

        self.health_roll = '1d6'


class Warrior(Archetype):
    """Represents the Warrior archetype."""
    def __init__(self):
        super(Warrior, self).__init__()
        self.name = 'Warrior'
        self.desc = fill(
            "|cWarriors|n are individual soldiers, mercenaries, bounty "
            "hunters or various types of combatants. They believe no "
            "problem can't be solved with their melee weapon and choose "
            "strength as their highest primary trait."
        )

        # set starting trait values
        self.traits['STR']['base'] = 6
        self.traits['DEX']['base'] = 4
        self.traits['CHA']['base'] = 4
        self.traits['VIT']['base'] = 6
        self.traits['REFL']['mod'] = -2
        self.traits['PP']['base'] = 2
        self.traits['MV']['base'] = 5

        self.health_roll = '1d6+1'
