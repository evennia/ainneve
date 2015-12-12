"""
Chargen EvMenu module.
"""
from evennia.utils import fill, dedent
from evennia.utils.evtable import EvTable
from world import archetypes, races, skills
from world.rulebook import d_roll
from evennia.utils.spawner import spawn
from math import ceil
import re


# Organize starter equipment prototypes by category
EQUIPMENT_CATEGORIES = {
    'Melee Weapons':
        (0, 'HAND_AXE', 'BATTLE_AXE', 'MAUL_HAMMER', 'LANCE_POLEARM',
         'PIKE_POLEARM', 'MAPLE_STAFF', 'MACE_ROD', 'MORNINGSTAR_ROD',
         'SCYTHE', 'SHORT_SWORD', 'RAPIER', 'WHIP'),
    'Ranged Weapons':
        (1, 'LONG_BOW', 'HAND_CROSSBOW', 'LIGHT_CROSSBOW'),
    'Ammunition':
        (5, 'ARROW_BUNDLE', 'QUARREL_BUNDLE'),
    'Thrown Weapons':
        (2, 'THROWING_AXE', 'THROWING_DAGGER', 'JAVELIN', 'TRIDENT'),
    'Armor':
        (3, 'CLOTH_GARMENT', 'LEATHER_GARMENT', 'BRIGANDINE', 'CHAIN_MAIL',
         'PLATED_MAIL', 'IRON_SCALE', 'IRON_BANDED'),
    'Shields':
        (4, 'BUCKLER_SHIELD', 'HERALDIC_SHIELD', 'TOWER_SHIELD'),
}
RE_ARTCL = re.compile(r'^an?\s', re.IGNORECASE)


def menunode_welcome_archetypes(caller):
    """Starting page and Archetype listing."""
    text = dedent("""\
        |wWelcome to |mAinneve|n, the example game for |yEvennia|n.

        To begin, select an |cArchetype|n. There are three base
        archetypes to choose from, plus three dual archetypes which
        combine the strengths and weaknesses of two archetypes into one.
    """)
    help = fill("In |mAinneve|n, character |cArchetypes|n represent the "
                "characters' class or primary role. The various archetypes "
                "have different bonuses and detriments, which are reflected "
                "in the character's starting traits.")
    options = []
    for arch in archetypes.VALID_ARCHETYPES:
        a = archetypes.load_archetype(arch)
        options.append({"desc": "{:40.40s}...".format(a.desc),
                        "goto": "menunode_select_archetype"})
    return (text, help), options


def menunode_select_archetype(caller, raw_input):
    """Archetype detail and selection menu node."""
    arch = archetypes.VALID_ARCHETYPES[int(raw_input)-1]
    arch = archetypes.load_archetype(arch)
    text = arch.ldesc + "Would you like to become this archetype?"
    options = ({"key": ("Yes", "ye", "y"),
                "desc": "Become {} {}".format("an" if arch.name[0] == 'A'
                                              else "a",
                                              arch.name),
                "exec": lambda c: archetypes.apply_archetype(c, arch.name,
                                                             reset=True),
                "goto": "menunode_allocate_traits"},
               {"key": ("No", "n", "_default"),
                "desc": "Return to Archetype selection",
                "goto": "menunode_welcome_archetypes"})
    return text, options


def menunode_allocate_traits(caller, raw_input):
    """Discretionary trait point allocation menu node."""
    text = ""
    if raw_input.isdigit() and int(raw_input) <= len(archetypes.PRIMARY_TRAITS):
        chartrait = caller.traits[archetypes.PRIMARY_TRAITS[int(raw_input)-1]]
        if chartrait.actual < 10:
            chartrait.mod += 1
        else:
            text += "|rCannot allocate more than 10 points to one trait!|n\n"

    data = []
    for i in xrange(3):
        data.append([_format_trait_3col(caller.traits[t])
                     for t in archetypes.PRIMARY_TRAITS[i::3]])
    table = EvTable(header=False, table=data)
    remaining = archetypes.get_remaining_allocation(caller.traits)

    text += "Allocate additional trait points as you choose.\n"
    text += "Current:\n{}".format(table)
    text += "\n  |w{}|n Points Remaining\n".format(remaining)
    text += "Please select a trait to increase:"

    help = "Traits:\n"
    help += "  Strength - affects melee attacks, fortitude saves, and physical tasks\n"
    help += "  Perception - affects ranged attacks, reflex saves, and perception tasks\n"
    help += "  Intelligence - affects skill bonuses, will saves, and magic\n"
    help += "  Dexterity - affects unarmed attacks, defense, and dexterity-based skills\n"
    help += "  Charisma - affects skills related to interaction with others\n"
    help += "  Vitality - affects health and stamina points"

    options = [{"desc": caller.traits[t].name,
                "goto": "menunode_allocate_traits"}
               for t in archetypes.PRIMARY_TRAITS]
    options.append({"desc": "Start Over",
                    "exec": lambda caller: archetypes.apply_archetype(caller,
                                                                      caller.db.archetype,
                                                                      reset=True),
                    "goto": "menunode_allocate_traits"})

    if remaining > 0:
        return (text, help), options
    else:
        return menunode_races(caller, "Final Skills:\n{}".format(table))


def menunode_races(caller, raw_input):
    """Race listing menu node."""
    text = ""
    if raw_input and raw_input[0] == 'F':
        text += raw_input

    text += "\n\nNext, select a race for your character."

    help = fill("Your race gives your character certain bonuses and"
                "detriments, and makes certain 'focuses' available. "
                "Select a race by number to see its details.")
    options = []
    for r in races.ALL_RACES:
        race = races.load_race(r)
        options.append({"desc": "{:<40.40s}...".format(race._desc),
                        "goto": "menunode_race_and_focuses"})
    return (text, help), options


def menunode_race_and_focuses(caller, raw_input):
    """Race detail and focus listing menu node."""
    race = races.ALL_RACES[int(raw_input)-1]
    race = races.load_race(race)
    text = race.desc + "Select a focus below to continue."
    help = fill("After selecting a focus, you will be prompted "
                "to save your race/focus combination.")
    def save_race(caller):
        caller.ndb.race = race

    options = [{"desc": f.name,
                "exec": save_race,
                "goto": "menunode_select_race_focus"}
               for f in race.foci]
    options.append({"desc": "Return to Race selection",
                    "goto": "menunode_races"})

    return (text, help), options


def menunode_select_race_focus(caller, raw_input):
    """Focus detail and final race/focus selection menu node."""
    race = caller.ndb.race
    focus = race.foci[int(raw_input)-1]
    text = "|wRace|n: |g{}|n\n|wFocus|n: ".format(race.name)
    text += focus.desc
    text += "Confirm this Race and Focus selection?"

    def del_race(caller):
        del caller.ndb.race

    options = ({"key": ("Yes", "ye", "y"),
                "desc": "Become {} {} with the {} focus".format(
                    'an' if race.name[0] == 'E' else 'a',
                    race.name,
                    focus.name),
                "exec": lambda char: races.apply_race(char, race, focus),
                "goto": "menunode_allocate_mana"},
               {"key": ("No", "n", "_default"),
                "desc": "Return to Race selection",
                "exec": del_race,
                "goto": "menunode_races"})

    return text, options


def menunode_allocate_mana(caller, raw_input):
    """Mana point allocation menu node."""
    tr = caller.traits
    manas = ('WM', 'BM')
    if raw_input.isdigit() and int(raw_input) <= len(manas):
        tr[manas[int(raw_input)-1]].base += 1

    remaining = tr.MAG.actual - sum(tr[m].base for m in manas)
    if remaining:
        text = "Your |CMagic|n trait is |w{}|n.\n\n".format(tr.MAG.actual)
        text += "This allows you to allocate that many points to your\n"
        text += "|wWhite Mana|n and |xBlack Mana|n counters.\n"
        text += "Current Values:\n"
        text += "  |wWhite Mana|n: |w{}|n\n".format(tr.WM.base)
        text += "  |xBlack Mana|n: |w{}|n\n".format(tr.BM.base)
        text += "You have |w{}|n points remaining. ".format(remaining)
        text += "Select a mana counter to increase:"
        help = "Magic users spend Mana points when casting spells. Different\n"
        help += "colors of magic require different colors of mana. The effects of\n"
        help += "different magics vary by color.\n\n"
        help += "  White - white magic spells are generally support/healing based\n"
        help += "  Black - black magic spells are generally attack-oriented\n\n"
        help += "The number of points allocated here determines the number of\n"
        help += "each color mana that will be spawned each turn of the game."
        options = [{"desc": tr[m].name,
                    "goto": "menunode_allocate_mana"}
                   for m in manas]

        def reset_mana(char):
            for m in manas:
                char.traits[m].base = 0

        options.append({"desc": "Start Over",
                        "exec": reset_mana,
                        "goto": "menunode_allocate_mana"})
        return (text, help), options
    else:
        if tr.MAG.actual > 0:
            output = "Final Mana Values:\n"
            output += "  |wWhite Mana|n: |w{}|n\n".format(tr.WM.actual)
            output += "  |xBlack Mana|n: |w{}|n\n\n".format(tr.BM.actual)
        else:
            output = ""
        skills.apply_skills(caller)
        return menunode_allocate_skills(caller, output)


def menunode_allocate_skills(caller, raw_input):
    """Skill -1 counter allocation menu node."""
    sk = caller.skills
    total = 3
    counts = {1: 'one', 2: 'two', 3: 'three'}

    minuses = (ceil(caller.traits.INT.actual / 3.0) -
               sum(sk[s].minus for s in skills.ALL_SKILLS))
    plusses = total - sum(sk[s].plus for s in skills.ALL_SKILLS)

    text = ""
    if raw_input.isdigit() and int(raw_input) <= len(skills.ALL_SKILLS):
        skill = sk[skills.ALL_SKILLS[int(raw_input)-1]]
        if minuses:
            if skill.actual - skill.minus - 1 > 0:
                skill.minus += 1
                minuses -= 1
            else:
                text += "|rSkills cannot be reduced below one.|n\n"
        elif plusses:
            if skill.actual + skill.plus + 1 <= 10:
                skill.plus += 1
                plusses -= 1
            else:
                text += "|rSkills cannot be increased above ten.|n\n"

    if plusses or minuses:
        text += raw_input if raw_input and raw_input[0] == 'F' else ""
        text += "Your ability to perform actions in Ainneve is\n"
        text += "tied to your character's skills. Your current skills:\n"

        data = []
        for i in xrange(3):
            data.append([_format_skill_3col(sk[s])
                         for s in skills.ALL_SKILLS[i::3]])
        table = EvTable(header=False, table=data)

        text += "{}\n".format(table)
        if minuses:
            text += "Please allocate |w{}|n |m'-1'|n counter{}.".format(
                        counts[minuses],
                        's' if minuses != 1 else '')
        elif plusses:
            text += "Please allocate |w{}|n |m'+1'|n counter{}.".format(
                        counts[plusses],
                        's' if plusses != 1 else '')

        help = "Skill allocation is a two step process. First, you\n"
        help += "distribute three '-1' counters across your skills,\n"
        help += "then a number of '+1' counters equal to your Intelligence\n"
        help += "divided by 3."

        options = [{"desc": sk[s].name,
                    "goto": "menunode_allocate_skills"}
                   for s in skills.ALL_SKILLS]

        def clear_skills(c, i):
            """Reset plus and minus counters on all skills."""
            for s in skills.ALL_SKILLS:
                sk[s].plus = 0
                sk[s].minus = 0

        options.append({"desc": "Start Over",
                        "exec": clear_skills,
                        "goto": "menunode_allocate_skills"})
        return (text, help), options
    else:
        skills.finalize_skills(caller.skills)
        data = []
        for i in xrange(3):
            data.append([_format_trait_3col(sk[s], color='|M')
                         for s in skills.ALL_SKILLS[i::3]])
        table = EvTable(header=False, table=data)
        output = "Final Skills:\n"
        output += "{skills}\n"
        output += "You get |w{coins}|n SC (Silver Coins) to start out.\n"

        caller.db.wallet['SP'] = d_roll('2d6+3')

        return menunode_equipment_cats(
            caller,
            output.format(skills=table,
                          coins=caller.db.wallet['SP'])
        )


def menunode_equipment_cats(caller, raw_input):
    """Initial equipment "shopping" - choose a category"""
    text = raw_input if raw_input and raw_input[0] == 'F' else ""
    text += "Select a category of equipment to view."
    category_list = sorted(EQUIPMENT_CATEGORIES.iterkeys(),
                           key=lambda c: EQUIPMENT_CATEGORIES[c][0])
    options = [{"desc": cat, "goto": "menunode_equipment_list"}
               for cat in category_list]
    return (text, help), options


def menunode_equipment_list(caller, raw_input):
    """Initial equipment "shopping" - list items in a category"""
    text = "Select an item to view details and buy."

    category_list = sorted(EQUIPMENT_CATEGORIES.iterkeys(),
                           key=lambda c: EQUIPMENT_CATEGORIES[c][0])
    category = ''
    if raw_input.isdigit() and int(raw_input) <= len(category_list):
        category = category_list[int(raw_input)-1]
    prototypes = spawn(return_prototypes=True)
    options = []
    for proto in EQUIPMENT_CATEGORIES[category][1:]:
        def save_item(char):
            char.ndb.item_prototype = proto

        options.append({
            "key": [RE_ARTCL.sub('', prototypes[proto]["key"]).title()] +
                   prototypes[proto].get("aliases", []),
            "desc": _format_menuitem_desc(prototypes[proto]),
            "exec": save_item,
            "goto": "menunode_examine_and_buy"
        })
    options.append({
        "key": ("Back", "_default"),
        "desc": "to category list",
        "goto": "menunode_equipment_cats",
    })
    return text, options


def menunode_examine_and_buy(caller, raw_input):
    """Examine and buy an item."""
    prototypes = spawn(return_prototypes=True)
    item = None
    if caller.ndb.item_prototype:
        item = prototypes[caller.ndb.item_prototype]
    text = ""
    if item:
        text += "|Y{name}|n\n"
        text += item['desc'] + '\n'
        stats = [["|C{:>10.10s}|n: |w{:>3}|n"],[]]

    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_character_desc(caller, raw_input):
    """Enter a character description."""

    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


def menunode_confirm(caller, raw_input):
    """Confirm and save allocations."""
    text = fill("")
    help = fill("")
    options = {}
    return (text, help), options


# helpers


def _format_trait_3col(trait, color='|C'):
    """Return a trait : value pair formatted for 3col layout"""
    return "{}{:<18.18}|n : |w{:>3}|n".format(
                color, trait.name, trait.actual)

def _format_skill_3col(skill):
    """Return a trait : value : counters triad formatted for 3col layout"""
    return "|M{:<15.15}|n: |w{:>3}|n (|m{:>+2}|n)".format(
                skill.name, skill.actual, skill.plus - skill.minus
           )

def _format_menuitem_desc(item):
    """Returns a piece of equipment formatted as a one-line menu item."""
    template = "{desc:27.27s}... "
    if item['typeclass'] in ("typeclasses.weapons.Weapon",
                             "typeclasses.weapons.TwoHandedWeapon",
                             "typeclasses.weapons.RangedWeapon",
                             "typeclasses.weapons.TwoHandedRanged"):
        template += "|c{handed}H|n [|rDmg: {damage}|n]"

    elif item['typeclass'] in ("typeclasses.armors.Shield",):
        template += "|c{handed}H|n [|yDef: {toughness}|n]"

    elif item['typeclass'] in ("typeclasses.armors.Armor",):
        template += "[|yDef: {toughness}|n]"

    return template.format(
        desc=item.get('desc', ''),
        handed=2 if 'TwoHanded' in item['typeclass'] else 1,
        damage=item.get('damage', ''),
        toughness=item.get('toughness', '')
    )
