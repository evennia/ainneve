"""
Combat commands.
"""

from evennia import default_cmds, CmdSet, create_script
from evennia.contrib.rpsystem import CmdEmote, CmdPose, CmdSay
from evennia.utils.utils import inherits_from
from evennia.utils.evtable import EvTable
from commands.equip import CmdInventory

# cmdsets


class InitCombatCmdSet(CmdSet):
    """Command set containing combat starting commands"""
    key = 'combat_init_cmdset'
    priority = 1
    mergetype = 'Union'

    def at_cmdset_creation(self):
        self.add(CmdInitiateAttack())


class CombatBaseCmdSet(CmdSet):
    """Command set containing always-available commands"""
    key = 'combat_base_cmdset'
    priority = 10
    mergetype = 'Replace'
    no_exits = True

    def at_cmdset_creation(self):
        inv = CmdInventory()
        inv.help_category = 'free instant actions'
        self.add(inv)

        say = CmdSay()
        say.help_category = 'free instant actions'
        self.add(say)

        emote = CmdEmote()
        emote.help_category = 'free instant actions'
        self.add(emote)

        pose = CmdPose()
        pose.help_category = 'free instant actions'
        self.add(pose)

        self.add(CmdCombatLook())
        self.add(default_cmds.CmdHelp())

        # admin/builder commands
        self.add(default_cmds.CmdScripts())
        self.add(default_cmds.CmdPy())


class CombatCmdSet(CmdSet):
    """Command set containing combat commands"""
    key = "combat_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdActionList())
        self.add(CmdCancelAction())
        self.add(CmdDropItem())
        self.add(CmdGetItem())
        self.add(CmdEquip())
        self.add(CmdKick())
        self.add(CmdStrike())
        self.add(CmdDodge())
        self.add(CmdAdvance())
        self.add(CmdRetreat())
        self.add(CmdFlee())
        # self.add(CmdWrestle())
        # self.add(CmdTackle())


class MeleeWeaponCmdSet(CmdSet):
    """Command set containing melee weapon commands"""
    key = "melee_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        self.add(CmdAttackMelee())


class RangedWeaponCmdSet(CmdSet):
    """Command set containing ranged weapon commands"""
    key = "ranged_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        self.add(CmdAttackRanged())

# commands


class CmdInitiateAttack(default_cmds.MuxCommand):
    """
    initiate combat against an enemy

    Usage:
      attack <target>

    Begins or joins turn-based combat against the given enemy.
    """
    key = 'attack'
    aliases = ['att', 'battle', 'batt']
    locks = 'cmd:not in_combat()'
    help_category = 'combat'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attack <target>")
            return

        target = caller.search(self.args)
        if not target:
            return

        # for combat against yourself
        if target.id == caller.id:
            caller.msg("Combat against yourself is not supported.")
            return

        if not inherits_from(target, 'typeclasses.characters.Character'):
            caller.msg("Combat against {target} is not supported.".format(
                target=target.get_display_name(caller)))
            return

        if target.ndb.no_attack:
            caller.msg("You cannot attack {target} at this time.".format(
                target=target.get_display_name(caller)
            ))
            return

        if caller.location.tags.get('no_attack', None, category='flags'):
            caller.msg("Combat is not allowed in this location.")
            return

        # set up combat
        if target.ndb.combat_handler:
            # target is already in combat - join it
            target.ndb.combat_handler.add_character(caller)
            target.ndb.combat_handler.combat_msg(
                "{actor} joins combat!" ,
                actor=caller
            )
        else:
            # create a new combat handler
            chandler = create_script("typeclasses.combat_handler.CombatHandler")
            chandler.add_character(caller)
            chandler.add_character(target)
            caller.msg("You attack {}!".format(
                target.get_display_name(caller)))
            target.msg("{} attacks you!".format(
                caller.get_display_name(target)))
            for char in chandler.db.characters.values():
                char.execute_cmd("look")
            chandler.msg_all("The turn begins. Declare your actions!")


class CmdDropItem(default_cmds.MuxCommand):
    """
    drop an item onto the floor during combat

    Usage:
      drop <item>

    Drops the given item.

    This is a free combat action.
    """
    key = 'drop'
    aliases = []
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'free actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: drop <item>")
            return
        target = caller.search(
            self.args,
            candidates=self.caller.contents,
            nofound_string="Can't find {item} in your inventory.".format(
                item=self.args))

        if not target:
            return

        caller.ndb.combat_handler.add_action(
            action="drop",
            character=self.caller,
            target=target,
            duration=0)

        caller.msg(
            "You add 'drop {}' to the combat queue.".format(
                target.get_display_name(caller)))

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdAttack(default_cmds.MuxCommand):
    """implementation melee and ranged attack shared functionality"""
    key = 'attack'
    aliases = ['att']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller
        ch = caller.ndb.combat_handler
        combat_chars = ch.db.characters.values()

        attack_type = getattr(self, 'attack_type', 'attack')
        duration = getattr(self, 'duration', 1)
        target = None

        if not self.args:
            if len(combat_chars) == 2:
                target = [x for x in combat_chars if x.id != caller.id][0]
            else:
                caller.msg("Usage: {}[/s] <target>".format(attack_type))
                return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        target = target or caller.search(
            self.args,
            candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="{}{}".format(attack_type, switch),
                character=caller,
                target=target,
                duration=duration)

        if ok:
            caller.msg(
                "You add '{attack}{switch} {target}' to the combat queue.".format(
                    attack=attack_type,
                    switch=switch,
                    target=target.get_display_name(caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        ch.check_end_turn()


class CmdAttackMelee(CmdAttack):
    """
    attack an enemy with melee weapons

    Usage:
      attack[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes the given enemy with your current weapon.

    This is a half-turn combat action.
    """

    aliases = ['att', 'stab', 'slice', 'chop', 'slash', 'bash']

    def func(self):
        super(CmdAttackMelee, self).func()


class CmdAttackRanged(CmdAttack):
    """
    attack an enemy with ranged weapons

    Usage:
      attack[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes the given enemy with your current weapon.

    This is a half-turn combat action.
    """

    aliases = ['att', 'fire at', 'shoot']

    def func(self):
        super(CmdAttackRanged, self).func()


class CmdKick(CmdAttack):
    """
    attack an enemy by kicking

    Usage:
      kick[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Kicks give a +2 bonus to your attack, but if you miss,
    you suffer a -1 penalty to your defense for one turn.

    This is a full-turn combat action.
    """
    key = 'kick'
    aliases = ['boot', 'stomp']
    help_category = 'full turn actions'

    def func(self):
        self.attack_type = 'kick'
        self.duration = 2
        super(CmdKick, self).func()


class CmdStrike(CmdAttack):
    """
    attack an enemy with quick strikes

    Usage:
      strike[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes are fast and accurate punches using your fists
    and arms.

    This is a half-turn combat action, but if both
    hands are available, two strikes will be performed
    during that half-turn, allowing up to four attacks
    per turn.
    """
    key = 'strike'
    aliases = ['punch', 'hit']
    help_category = 'half turn actions'

    def func(self):
        self.attack_type = 'strike'
        super(CmdStrike, self).func()


class CmdDodge(default_cmds.MuxCommand):
    """
    dodge any incoming attack

    Usage:
      dodge

    Any incoming attackers make two attack rolls and
    keep the lower of the two, reducing your damage.

    This is a half-turn combat action.
    """
    key = 'dodge'
    aliases = ['duck']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        ok = caller.ndb.combat_handler.add_action(
                action="dodge",
                character=self.caller,
                target=self.caller,
                duration=1)
        if ok:
            caller.msg("You add 'dodge' to the combat queue.")
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdAdvance(default_cmds.MuxCommand):
    """
    move toward an opponent

    Usage:
      advance[/reach] [<target>]

    Switches:
      reach: advances only as far as 'reach' range,
             rather than 'melee'

    Moves your character from 'ranged' range to
    'melee' range with the specified opponent.

    This is a half-turn combat action.
    """
    key = 'advance'
    aliases = ['approach', 'adv', 'appr']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller
        combat_chars = caller.ndb.combat_handler.db.characters.values()
        target = None
        if not self.args:
            if len(combat_chars) == 2:
                target = [x for x in combat_chars if x.id != caller.id][0]
            else:
                caller.msg("Usage: advance[/reach] <target>")
                return

        target = target or caller.search(
                                self.args,
                                candidates=combat_chars)

        if not target:
            return

        sw_reach = "/reach" if any(sw.startswith("r") for sw
                                   in self.switches) else ""

        ok = caller.ndb.combat_handler.add_action(
                action="advance{}".format(sw_reach),
                character=caller,
                target=target,
                duration=1)
        if ok:
            caller.msg("You add 'advance{range} on {target}' to the combat queue.".format(
                range=" to reach" if sw_reach else "",
                target=target.get_display_name(caller)
            ))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
            caller.ndb.combat_handler.check_end_turn()


class CmdRetreat(default_cmds.MuxCommand):
    """
    move away from all opponents

    Usage:
      retreat[/reach]

    Switches:
      reach: retreats only as far as 'reach' range,
             rather than 'ranged'

    Attempts to moves your character away from all
    other combatants. If spaces is not specified, uses
    all available MV points.

    This is a half-turn combat action.
    """
    key = 'retreat'
    aliases = ['ret']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        sw_reach = "/reach" if any(sw.startswith("r") for sw
                                   in self.switches) else ""

        ok = caller.ndb.combat_handler.add_action(
                action="retreat{}".format(sw_reach),
                character=self.caller,
                target=self.caller,
                duration=1)
        if ok:
            caller.msg("You add 'retreat{range}' to the combat queue.".format(
                range=" to reach" if sw_reach else ""))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdGetItem(default_cmds.CmdGet):
    """
    get an item during combat

    Usage:
      get <obj>

    Switches:
      equip - Equips the object

    Picks up an object from your location and
    puts it in your inventory.

    This is a half-turn combat action.
    """
    key = 'get'
    aliases = ['grab', 'pick up']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: get <obj>")
            return

        target = caller.search(self.args)

        if not target:
            return

        if not target.access(caller, "get"):
            caller.msg("You cannot get {}.".format(
                target.get_display_name(caller)))
            return

        ok = caller.ndb.combat_handler.add_action(
                action="get",
                character=self.caller,
                target=target,
                duration=1)
        if ok:
            caller.msg("You add 'get {}' to the combat queue.".format(
                target.get_display_name(self.caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdEquip(default_cmds.MuxCommand):
    """
    equip a weapon or piece of armor

    Usage:
      equip
      equip <item>

    If no item is specified, displays your current equipment
    as a free action.

    Equips an item to its required slot(s), replacing any
    currently equipped item.

    This is a half-turn combat action.
    """
    key = 'equip'
    aliases = ['eq', 'wear', 'wield']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller
        if self.args:

            target = caller.search(self.args)

            if not target:
                return

            if not target.access(caller, "equip"):
                caller.msg("You cannot equip {}.".format(
                    target.get_display_name(caller)))
                return

            ok = caller.ndb.combat_handler.add_action(
                    action="equip",
                    character=self.caller,
                    target=target,
                    duration=1)

            if ok:
                caller.msg("You add 'equip {}' to the combat queue.".format(
                    target.get_display_name(caller)))
            else:
                caller.msg("You have already entered all actions for your turn.")

            # tell the handler to check if turn is over
            caller.ndb.combat_handler.check_end_turn()
        else:
            # no arguments; display current equip
            data = []
            s_width = max(len(s) for s in caller.equip.slots)
            for slot, item in caller.equip:
                if not item or not item.access(caller, 'view'):
                    continue
                stat = " "
                if item.attributes.has('damage'):
                    stat += "(|rDamage: {:>2d}|n) ".format(item.db.damage)
                if item.attributes.has('toughness'):
                    stat += "(|yToughness: {:>2d}|n)".format(item.db.toughness)
                if item.attributes.has('range'):
                    stat += "(|G{}|n) ".format(item.db.range.capitalize())

                data.append(
                    "  |b{slot:>{swidth}.{swidth}}|n: {item:<20.20} {stat}".format(
                        slot=slot.capitalize(),
                        swidth=s_width,
                        item=item.name,
                        stat=stat,
                    )
                )
            if len(data) <= 0:
                output = "You have nothing in your equipment."
            else:
                table = EvTable(header=False, border=None, table=[data])
                output = "|YYour equipment:|n\n{}".format(table)

            caller.msg(output)


class CmdWrestle(default_cmds.MuxCommand):
    """
    wrestle an opponent

    Usage:
      wrestle[/break] <target>

    Perform an unarmed attack against the target character
    that if successful, lowers the target's wrestling position
    one level. Wrestling positions go from

    Free standing -> clinching -> take down -> pinned

    Any combatant whose wrestling position is clinching or
    below can only defend and use the /break switch to
    attempt to raise their wrestling position.

    This is a full-turn combat action.
    """
    key = 'wrestle'
    aliases = ['grapple']
    locks = 'cmd:in_combat()'
    help_category = 'full turn actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: wrestle[/break] <target>")
            return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        combat_chars = caller.ndb.combat_handler.db.characters.values()

        target = caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="wrestle{}".format(switch),
                character=self.caller,
                target=target,
                duration=2)

        if ok:
            caller.msg(
                "You add 'wrestle{switch} {target}' to the combat queue".format(
                    switch=switch,
                    target=target.get_display_name(caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdTackle(default_cmds.MuxCommand):
    """
    tackle an opponent

    Usage:
      tackle <target>

    Attempt to rush an opponent to try and tackle them to the
    ground. A tackle must be started with at least 4 spaces
    distance between you and your target. If successful, lowers
    the target's wrestling position immediately to 'take down',

    This combat action takes a turn and a half to complete.
    """
    key = 'tackle'
    aliases = []
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'multi turn actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: tackle <target>")
            return

        combat_chars = caller.ndb.combat_handler.db.characters.values()

        target = caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="tackle",
                character=caller,
                target=target,
                duration=3,
                longturn=True)

        if ok:
            caller.msg(
                "You add 'tackle {target}' to the combat queue".format(
                    target=target.get_display_name(self.caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdFlee(default_cmds.MuxCommand):
    """
    escape from combat

    Usage:
      flee

    Attempt to disengage combat and leave the area. Success
    is governed by the escape skill as well as the distance from
    other combatants.

    This is a half-turn combat action.
    """
    key = 'flee'
    aliases = ['escape']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'full turn actions'

    def func(self):
        caller = self.caller

        ok = caller.ndb.combat_handler.add_action(
                action="flee",
                character=caller,
                target=caller,
                duration=2)
        if ok:
            caller.msg("You add 'flee' to the combat queue.")
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdCombatLook(default_cmds.MuxCommand):
    """
    assess the combat situation

    Usage:
      look

    Provides a summary of combat status, including opponents
    by range, remaining time to enter actions, and a listing
    of currently entered actions.
    """
    key = 'look'
    aliases = ['l', 'ls']
    locks = 'cmd:in_combat()'
    help_category = 'free instant actions'

    def func(self):
        caller = self.caller
        ch = caller.ndb.combat_handler

        caller.msg("You are in combat.")
        caller.msg("  Opponents:")
        opponents_by_range = ch.get_proximity(caller)
        for rng in opponents_by_range:
            for opp_id in opponents_by_range[rng]:
                opponent = ch.db.characters[opp_id]
                caller.msg(
                    "    {opponent} at |G{range}|n range.".format(
                        opponent=opponent.get_display_name(caller),
                        range=rng))

        if ch.is_active:
            caller.msg(
                "  The current turn timer has |y{}|n seconds remaining.".format(
                    ch.time_until_next_repeat()))
            if len(ch.db.turn_actions[caller.id]):
                caller.msg("  You have entered the following actions:")
                durations = ['free', 'half-turn', 'full-turn', 'multi-turn']
                for idx, (action, _, target, duration) \
                        in enumerate(ch.db.turn_actions[caller.id]):
                    duration = duration if duration < len(durations) \
                        else len(durations)-1
                    caller.msg(
                        "    {idx}: |w{action:<25}|n {target:<30} (|Y{duration} action|n)".format(
                            idx=idx+1,
                            action=action,
                            target='' if target == caller
                                   else target.get_display_name(caller),
                            duration=durations[duration]))


class CmdCancelAction(default_cmds.MuxCommand):
    """
    cancel a combat action

    Usage:
      cancel[/all]

    Switches:
      all: cancels all actions instead of last added

    Removes the last action or optionally all actions
    in the action queue for this turn.
    """
    key = 'cancel'
    aliases = ['can', 'cxl', 'x']
    locks = 'cmd:in_combat()'
    help_category = 'free instant actions'

    def func(self):
        caller = self.caller
        ch = caller.ndb.combat_handler

        if 'all' in self.switches:
            removed = True
            while removed:
                removed = ch.remove_last_action(caller)
            caller.msg('All combat actions have been canceled.')

        else:
            removed = ch.remove_last_action(caller)
            if removed:
                action, target = removed
                caller.msg('Canceled "{action}{target}" action.'.format(
                    action=action,
                    target='' if target == caller
                           else ' {}'.format(target.get_display_name(caller))
                ))
            else:
                caller.msg('You have not yet entered any actions this turn.')


class CmdActionList(default_cmds.MuxCommand):
    """
    list combat actions

    Usage:
      actions

    Displays a brief list of available actions.
    """
    key = 'actions'
    aliases = ['act list', 'actionlist']
    locks = 'cmd:in_combat()'
    help_category = 'help'

    def func(self):
        caller = self.caller

        output = """
|wCombat Actions
|C~~~~~~~~~~~~~~|n
  |cGeneral|n
  * |wlook|n          [|Yinstant|n]   |x-|n display opponents, their ranges, entered
                                actions, and time remaining in turn
  * |wflee|n          [|Yfull-turn|n] |x-|n attempt to escape from combat

  |cItem / Equipment|n
  * |wget <item>|n    [|Yhalf-turn|n] |x-|n get an item from the room
  * |wdrop <item>|n   [|Yfree|n]      |x-|n drop an item from equipment or inventory
  * |wequip <item>|n  [|Yhalf-turn|n] |x-|n equip an item from inventory
  * |wremove <item>|n [|Yhalf-turn|n] |x-|n remove an equipped item

  |cRange / Movement|n
  * |wadvance|n       [|Yhalf-turn|n] |x-|n advance toward an opponent
  * |wretreat|n       [|Yhalf-turn|n] |x-|n retreat from opponents

  |cAttacking|n
  * |wattack|n        [|Yhalf-turn|n] |x-|n attack with equipped melee or ranged weapon
  * |wkick|n          [|Yfull-turn|n] |x-|n powerful unarmed kicking attack
  * |wstrike|n        [|Yhalf-turn|n] |x-|n unarmed punching attack with free hand(s)

  |cDefending|n
  * |wdodge|n         [|Yhalf-turn|n] |x-|n attempt to dodge an opponent's attack

"""
        caller.msg(output)
