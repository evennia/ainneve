"""
Chargen EvMenu module.

The menu node functions defined in this module make up
the Ainneve character creation process, which is based
on a subset of Open Adventure rules.
"""
from evennia import spawn, TICKER_HANDLER as tickerhandler
from evennia.utils import fill, dedent
from evennia.utils.evtable import EvTable

from world import archetypes, races, skills
from world.rulebook import d_roll
from world.economy import format_coin as as_price
from world.economy import transfer_funds, InsufficientFunds

from math import ceil
import re


# Organize starter equipment prototypes by category
_EQUIPMENT_CATEGORIES = {
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
_CATEGORY_HELP = {
    'Melee Weapons':
        fill('These weapons are used in close combat. Their |rDamage|n '
             'statistic is added to your |CStrength|n trait to determine '
             'your attack score in combat.'),
    'Ranged Weapons':
        fill('These weapons require ammunition, and are used to attack from a '
             'distance. Their |rDamage\n statistic is added to your '
             '|CPerception|n trait to determine your attack score in combat.'),
    'Ammunition':
        'Ranged weapons require these items in order to attack.',
    'Thrown Weapons':
        fill('These ranged weapons do not require ammunition, as they are'
             'thrown at their target.'),
    'Armor':
        fill('Suited armor provides protection from damage. Their '
             '|yToughness|n statistic is added to your |CDexterity|n trait '
             'to determine your defense score in combat.'),
    'Shields':
        fill('Shields are pieces of armor that are wielded in an off-hand '
             'equipment slot.')
}

_CATEGORY_LIST = sorted(list(_EQUIPMENT_CATEGORIES.keys()), key=lambda c: _EQUIPMENT_CATEGORIES[c][0])


article_re = re.compile(r'^an?\s', re.IGNORECASE)


def menunode_welcome_archetypes(caller):
    """Starting page and Archetype listing."""
    text = dedent("""\
        |wWelcome to |mAinneve|w, the example game for |yEvennia|w.|n

        To begin, select an |cArchetype|n. There are three base
        archetypes to choose from, plus three dual archetypes which
        combine the strengths and weaknesses of two archetypes into one.

        Select an Archetype by number below to view its details, or |whelp|n
        at any time for more info.
    """)
    help = fill("In |mAinneve|n, character |cArchetypes|n represent the "
                "characters' class or primary role. The various archetypes "
                "have different strengths and weaknesses, which are reflected "
                "in your character's starting traits.")
    options = []
    for arch in archetypes.VALID_ARCHETYPES:
        a = archetypes.load_archetype(arch)
        options.append({"desc": "|c{}|n".format(a.name),
                        "goto": "menunode_select_archetype"})
    return (text, help), options


def menunode_select_archetype(caller, raw_string):
    """Archetype detail and selection menu node."""
    arch = archetypes.VALID_ARCHETYPES[int(raw_string.strip()) - 1]
    arch = archetypes.load_archetype(arch)
    text = arch.ldesc + "Would you like to become this archetype?"
    help = "Examine the properties of this archetype and decide whether\n"
    help += "to use its starting attributes for your character."
    options = ({"key": ("Yes", "ye", "y"),
                "desc": "Become {} {}".format("an" if arch.name[0] == 'A'
                                              else "a",
                                              arch.name),
                "exec": lambda s: archetypes.apply_archetype(s.new_char, arch.name,
                                                             reset=True),
                "goto": "menunode_allocate_traits"},
               {"key": ("No", "n", "_default"),
                "desc": "Return to Archetype selection",
                "goto": "menunode_welcome_archetypes"})
    return (text, help), options


def menunode_allocate_traits(caller, raw_string):
    """Discretionary trait point allocation menu node."""
    char = caller.new_char
    text = ""
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(archetypes.PRIMARY_TRAITS):
        chartrait = char.traits[archetypes.PRIMARY_TRAITS[int(raw_string) - 1]]
        if chartrait.actual < 10:
            chartrait.mod += 1
        else:
            text += "|rCannot allocate more than 10 points to one trait!|n\n"

    remaining = archetypes.get_remaining_allocation(char.traits)

    text += "Your character's traits influence combat abilities and skills.\n"
    text += "Type 'help' to see individual trait definitions.\n\n"
    text += "Allocate additional trait points as you choose.\n"
    text += "\n  |w{}|n Points Remaining\n".format(remaining)
    text += "Please select a trait to increase:"

    help = "Traits:\n"
    help += "  Strength - affects melee attacks, fortitude saves, and physical tasks\n"
    help += "  Perception - affects ranged attacks, reflex saves, and perception tasks\n"
    help += "  Intelligence - affects skill bonuses, will saves, and magic\n"
    help += "  Dexterity - affects unarmed attacks, defense, and dexterity-based skills\n"
    help += "  Charisma - affects skills related to interaction with others\n"
    help += "  Vitality - affects health and stamina points"

    options = [{"desc": _format_trait_opts(char.traits[t]),
                "goto": "menunode_allocate_traits"}
               for t in archetypes.PRIMARY_TRAITS]
    options.append({"desc": "Start Over",
                    "exec": lambda s: archetypes.apply_archetype(
                                          char,
                                          char.db.archetype,
                                          reset=True),
                    "goto": "menunode_allocate_traits"})

    if remaining > 0:
        return (text, help), options
    else:
        data = []
        for i in list(range(3)):
            data.append([_format_trait_opts(char.traits[t])
                         for t in archetypes.PRIMARY_TRAITS[i::3]])
        table = EvTable(header=False, table=data)
        return menunode_races(caller, "Final Skills:\n{}".format(table))


def menunode_races(caller, raw_string):
    """Race listing menu node."""
    text = ""
    if raw_string and raw_string[0] == 'F':
        text += raw_string

    text += "\n\nNext, select a race for your character:"

    help = fill("Your race gives your character certain bonuses and "
                "detriments, and makes certain 'focuses' available. "
                "Select a race by number to see its details.")
    options = []
    for r in races.ALL_RACES:
        race = races.load_race(r)
        options.append({"desc": "{:<40.40s}...".format(race._desc),
                        "goto": "menunode_race_and_focuses"})
    return (text, help), options


def menunode_race_and_focuses(caller, raw_string):
    """Race detail and focus listing menu node."""
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(races.ALL_RACES):
        race = races.ALL_RACES[int(raw_string) - 1]
        race = races.load_race(race)
        caller.ndb._menutree.race = race

    race = caller.ndb._menutree.race

    text = race.desc + "Select a focus below to continue:"
    help = fill("After selecting a focus, you will be prompted "
                "to save your race/focus combination.")

    options = [{"desc": f.name,
                "goto": "menunode_select_race_focus"}
               for f in race.foci]
    options.append({"key": ("Back", "_default"),
                    "desc": "Return to Race selection",
                    "goto": "menunode_races"})

    return (text, help), options


def menunode_select_race_focus(caller, raw_string):
    """Focus detail and final race/focus selection menu node."""
    char = caller.new_char
    race = caller.ndb._menutree.race
    focus = race.foci[int(raw_string.strip()) - 1]
    text = "|wRace|n: |g{}|n\n|wFocus|n: ".format(race.name)
    text += focus.desc
    text += "Confirm this Race and Focus selection?"
    help = "Examine the bonuses and detriments of this race and focus combination\n"
    help += "and decide whether to apply them to your character."

    options = ({"key": ("Yes", "ye", "y"),
                "desc": "Become {} {} with the {} focus".format(
                    'an' if race.name[0] == 'E' else 'a',
                    race.name,
                    focus.name),
                "exec": lambda s: races.apply_race(char, race, focus),
                "goto": "menunode_allocate_mana"},
               {"key": ("No", "n", "_default"),
                "desc": "Return to {} details".format(race.name),
                "goto": "menunode_race_and_focuses"})

    return (text, help), options


def menunode_allocate_mana(caller, raw_string):
    """Mana point allocation menu node."""
    char = caller.new_char
    tr = char.traits
    manas = ('WM', 'BM')
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(manas):
        tr[manas[int(raw_string) - 1]].base += 1

    remaining = tr.MAG.actual - sum(tr[m].base for m in manas)
    if remaining:
        text = "Your |CMagic|n trait is |w{}|n.\n\n".format(tr.MAG.actual)
        text += "This allows you to allocate that many points to your\n"
        text += "|wWhite Mana|n and |xBlack Mana|n counters.\n"
        text += "You have |w{}|n points remaining. ".format(remaining)
        text += "Select a mana counter to increase:"
        help = "Magic users spend Mana points when casting spells. Different\n"
        help += "colors of magic require different colors of mana. The effects of\n"
        help += "different magics vary by color.\n\n"
        help += "  White - white magic spells are generally support/healing based\n"
        help += "  Black - black magic spells are generally attack-oriented\n\n"
        help += "The number of points allocated here determines the number of\n"
        help += "each color mana that will be spawned each turn of the game."
        options = [{"desc": _format_trait_opts(tr[m], '|w' if m == 'WM' else '|x'),
                    "goto": "menunode_allocate_mana"}
                   for m in manas]

        def reset_mana(s):
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
            output += "  |xBlack Mana|n: |w{}|n\n".format(tr.BM.actual)
        else:
            output = ""
        # TODO: implement spells; add level 0 spell cmdsets here

        archetypes.calculate_secondary_traits(char.traits)
        archetypes.finalize_traits(char.traits)
        tickerhandler.add(interval=6, callback=char.at_turn_start)
        skills.apply_skills(char)
        return menunode_allocate_skills(caller, output)


def menunode_allocate_skills(caller, raw_string):
    """Skill -1 counter allocation menu node."""
    char = caller.new_char
    sk = char.skills
    total = 3
    counts = {1: 'one', 2: 'two', 3: 'three'}

    plusses = (ceil(char.traits.INT.actual / 3.0) -
               sum(sk[s].plus for s in skills.ALL_SKILLS))
    minuses = total - sum(sk[s].minus for s in skills.ALL_SKILLS)

    text = ""
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(skills.ALL_SKILLS):
        skill = sk[skills.ALL_SKILLS[int(raw_string) - 1]]
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
        text += "{}\n\n".format(raw_string) if raw_string and raw_string[0] == 'F' else ""
        text += "Your ability to perform actions in Ainneve is\n"
        text += "tied to your character's skills.\n"

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

        options = [{"desc": _format_skill_opts(sk[s]),
                    "goto": "menunode_allocate_skills"}
                   for s in skills.ALL_SKILLS]

        def clear_skills(s):
            """Reset plus and minus counters on all skills."""
            for skill in skills.ALL_SKILLS:
                sk[skill].plus = 0
                sk[skill].minus = 0

        options.append({"desc": "Start Over",
                        "exec": clear_skills,
                        "goto": "menunode_allocate_skills"})
        return (text, help), options
    else:
        skills.finalize_skills(char.skills)
        data = []
        for i in list(range(3)):
            data.append([_format_trait_opts(sk[s], color='|M')
                         for s in skills.ALL_SKILLS[i::3]])
        table = EvTable(header=False, table=data)
        output = "Final Skills:\n"
        output += "{skills}\n"

        char.db.wallet['SC'] = d_roll('2d6+3')
        output += "You begin with |w{sc} SC|n (Silver Coins)."

        return menunode_equipment_cats(
            caller,
            output.format(skills=table, sc=char.db.wallet['SC'])
        )


def menunode_equipment_cats(caller, raw_string):
    """Initial equipment "shopping" - choose a category"""
    text = raw_string if raw_string and raw_string[0] == 'F' else ""
    text += "\n\nNext, purchase your starting equipment.\n"
    text += "You have |w{coins}|n.\n"
    text += "Select a category of equipment to view:"
    text = text.format(coins=as_price(caller.new_char.db.wallet))

    help = fill("Equipment is grouped into categories. Select one to view"
                "the items in that category.")
    help += "\n\n"
    help += fill("Money in Ainneve is represented as Copper Coins (CC),"
                 "Silver Coins (SC), and Gold Coins (GC), with a conversion"
                 "rate of 100 CC = 1 SC and 100 SC = 1 GC")

    def show_inventory(session):
        """display the character's inventory

        We achieve this by "monkey patching" the session's `msg` method
        onto the new char to catch the output of the 'inventory' command.
        """
        session.msg('\n')
        old_msg = session.new_char.msg
        session.new_char.msg = session.msg
        session.new_char.execute_cmd('inventory')
        session.new_char.msg = old_msg

    options = [{"desc": cat, "goto": "menunode_equipment_list"}
               for cat in _CATEGORY_LIST]

    options.append({"key": ("Inventory", "inv", "i"),
                    "desc": "Show your current inventory",
                    "exec": show_inventory,
                    "goto": "menunode_equipment_cats"})

    options.append({"key": "Done",
                    "desc": "Continue to character description",
                    "goto": "menunode_character_sdesc"})

    return (text, help), options


def menunode_equipment_list(caller, raw_string):
    """Initial equipment "shopping" - list items in a category"""
    text = "You currently have {}.\n".format(as_price(caller.new_char.db.wallet))
    text += "Select an item to view details and buy:"
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(_CATEGORY_LIST):
        caller.ndb._menutree.item_category = _CATEGORY_LIST[int(raw_string) - 1]

    category = (caller.ndb._menutree.item_category
                if hasattr(caller.ndb._menutree, 'item_category')
                else '')

    help = _CATEGORY_HELP[category]
    prototypes = spawn(return_parents=True)
    options = []
    for proto in _EQUIPMENT_CATEGORIES[category][1:]:
        options.append({
            "desc": _format_menuitem_desc(prototypes[proto.lower()]),
            "goto": "menunode_examine_and_buy"
        })
    options.append({
        "key": ("Back", "_default"),
        "desc": "to category list",
        "goto": "menunode_equipment_cats",
    })
    return (text, help), options


def menunode_examine_and_buy(caller, raw_string):
    """Examine and buy an item."""
    char = caller.new_char
    prototypes = spawn(return_parents=True)
    items, item = _EQUIPMENT_CATEGORIES[caller.ndb._menutree.item_category][1:], None
    raw_string = raw_string.strip()
    if raw_string.isdigit() and int(raw_string) <= len(items):
        item = prototypes[items[int(raw_string) - 1].lower()]
    if item:
        text = _format_item_details(item)
        text += "You currently have {}. Purchase |w{}|n?".format(
                    as_price(char.db.wallet),
                    item['key']
                )
        help = "Choose carefully. Purchases are final."

        def purchase_item(session):
            """Process item purchase."""
            try:
                # this will raise exception if caller doesn't
                # have enough funds in their `db.wallet`
                print(item)
                transfer_funds(char, None, item['value'])
                ware = spawn(item).pop()
                ware.move_to(char, quiet=True)
                ware.at_get(char)
                rtext = "You pay {} and purchase {}".format(
                            as_price(ware.db.value),
                            ware.key
                         )
            except InsufficientFunds:
                rtext = "You do not have enough money to buy {}.".format(
                            item['key'])
            session.msg(rtext)

        options = ({"key": ("Yes", "ye", "y"),
                    "desc": "Purchase {} for {}".format(
                               item['key'],
                               as_price(item['value'])
                            ),
                    "exec": purchase_item,
                    "goto": "menunode_equipment_cats"},
                   {"key": ("No", "n", "_default"),
                    "desc": "Go back to category list",
                    "goto": "menunode_equipment_list"}
                   )

        return (text, help), options
    else:
        assert False


def menunode_character_sdesc(caller, raw_string):
    """Enter a character description."""
    text = "First, enter a short description for your character. It will be\n" \
           "shown in place of your name to those who don't know you, so it should\n" \
           "be general, like, 'a tall man', 'a hardened warrior', or 'a crazy old coot'."
    help = fill("After character creation, the short description can be modified using "
                "the '@desc' command. Also, see 'help recog' for information on using the "
                "recog command to set recognition descriptions in place of other characters' "
                "short descriptions.")
    options = [{"key": "_default",
                "goto": "menunode_character_desc"}]
    return (text, help), options


def menunode_character_desc(caller, raw_string):
    """Enter a character description."""
    # add the previously entered description to the sdesc handler
    char = caller.new_char
    char.sdesc.add(raw_string)
    # prompt for desc property
    text = "Enter a more detailed description of your character's appearance. This will be\n" \
           "displayed when others look at your character explicitly."
    help = fill("After character creation, your character's long description can be modified"
                "using the '@desc' command.")
    options = [{"key": "_default",
                "goto": "menunode_confirm"}]
    return (text, help), options


def menunode_confirm(caller, raw_string):
    """Confirm and save allocations."""
    char = caller.new_char
    char.db.desc = str(raw_string)

    old_msg = char.msg
    char.msg = caller.msg
    char.execute_cmd('sheet/skills')
    char.msg = old_msg

    text = "Save your character with skills and traits above\n"
    text += "and exit character generation?"
    help = "If you have made any mistakes along the way, now is your chance\n"
    help += "to start from scratch and correct them."

    def reset_all(s):
        """Reset a character before starting over."""
        (char.db.archetype,
         char.db.race,
         char.db.focus,
         char.db.desc) = [None for _ in list(range(4))]

        char.sdesc.add('a normal person')
        char.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}
        char.traits.clear()
        char.skills.clear()
        for item in char.contents:
            item.delete()

    options = [{"key": ("Yes", "ye", "y"),
                "desc": "Save your character and enter |mAinneve|n",
                "goto": "menunode_end"},
               {"key": ("No", "n"),
                "desc": "Start over from the beginning",
                "exec": reset_all,
                "goto": "menunode_welcome_archetypes"}]
    return text, options


def menunode_end(caller, raw_string):
    """Farewell message."""
    caller.new_char.db.chargen_complete = True
    text = dedent("""
        Congratulations!

        You have completed |mAinneve|n character creation.
        This could be some more informative message eventually...""")
    return text, None


# helpers


def _format_trait_opts(trait, color='|C'):
    """Return a trait : value pair formatted as a menu option"""
    return "{}{:<15.15}|n : |x[|n{:>4}|x]|n".format(
                color, trait.name, trait.actual)


def _format_skill_opts(skill):
    """Return a trait : value : counters triad formatted as a menu option"""
    return "|M{:<15.15}|n: |w{:>4}|n (|m{:>+2}|n)".format(
                skill.name,
                skill.actual + skill.plus - skill.minus,
                skill.plus - skill.minus)


def _format_menuitem_desc(item):
    """Returns a piece of equipment formatted as a one-line menu item."""
    template = "|w{name}|n Cost: ({price}) "
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
        name=article_re.sub('', item['key']).title(),
        price=as_price(item.get('value', {})),
        handed=2 if 'TwoHanded' in item['typeclass'] else 1,
        damage=item.get('damage', ''),
        toughness=item.get('toughness', '')
    )


def _format_item_details(item):
    print(item)
    # The hackiest solution in the world
    # Todo: Evaluate replacing this method
    value = [i for i in item['attrs'] if i[0] == 'value'][0][1]
    weight = [i for i in item['attrs'] if i[0] == 'weight'][0][1]
    """Returns a piece of equipment's details and description."""
    stats = [["          |CPrice|n: {}".format(as_price(value)),
              "         |CWeight|n: |w{}|n".format(weight)],
             []]
    col1, col2 = stats
    # this is somewhat awkward because we're using prototype dicts instead
    # of instances of these classes.
    if item['typeclass'] in ("typeclasses.weapons.Weapon",
                             "typeclasses.weapons.TwoHandedWeapon",
                             "typeclasses.weapons.RangedWeapon",
                             "typeclasses.weapons.TwoHandedRanged",
                             "typeclasses.armors.Shield"):
        col2.append("     |CHandedness|n: |c{}H|n".format(
            2 if 'TwoHanded' in item['typeclass'] else 1
        ))

    if item['typeclass'] in ("typeclasses.weapons.Weapon",
                             "typeclasses.weapons.TwoHandedWeapon",
                             "typeclasses.weapons.RangedWeapon",
                             "typeclasses.weapons.TwoHandedRanged"):
        col2.append("         |CDamage|n: |r{}|n".format(item['damage']))

    if item['typeclass'] in ("typeclasses.weapons.RangedWeapon",
                             "typeclasses.weapons.TwoHandedRanged"):
        col2.append("          |CRange|n: |G{}|n".format(
            ", ".join([r.capitalize() for r in item['range']])))

    if item['typeclass'] in ("typeclasses.armors.Armor",
                             "typeclasses.armors.Shield"):
        col2.append("      |CToughness|n: |y{}|n".format(item['toughness']))

    if 'quantity' in item:
        col2.append("       |CQuantity|n: |w{}|n".format(item['quantity']))

    table = EvTable(header=False, table=stats, border=None)

    text = "|Y{name}|n\n"
    text += "{desc}\n"
    text += "{stats}\n"
    if 'ammunition' in item:
        text += "  This weapon requires ammunition: |w{ammo}|n\n"

    return text.format(name=item['key'].title(),
                       desc=fill(item['desc']),
                       stats=table,
                       ammo=item.get('ammunition', ''))
