"""
Combat commands


"""

from evennia import default_cmds, CmdSet
from evennia.contrib.rpsystem import CmdEmote, CmdPose
from .equip import CmdEquip as EQUIP_CMD

# cmdsets


class CombatCmdSet(CmdSet):
    """Command set containing combat commands"""
    key = "combat_cmdset"
    priority = 10
    mergetype = "Replace"
    no_exits = True

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(default_cmds.CmdSay())
        self.add(CmdEmote())
        self.add(CmdPose())


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
    aliases = ['battle']
    help_category = 'combat'

    def func(self):
        pass


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
    help_category = 'combat'

    def func(self):
        if not self.args:
            self.caller.msg("Usage: drop <item>")
            return
        target = self.caller.search(self.args)
        if not target:
            return
        self.caller.ndb.combat_handler.add_action(
            action="drop",
            character=self.caller,
            target=target,
            duration=0)

        self.caller.msg(
            "You add 'drop {}' to the combat queue".format(
                target.get_display_name(self.caller)))

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdLieProne(default_cmds.MuxCommand):
    """
    lie on the ground prone

    Usage:
      lie [prone]

    Causes you to take a position lying on the ground face
    down. This gives a +2 defense buff against ranged attacks,
    but a -2 defense penalty against melee attacks.

    This is a free combat action.
    """
    key = 'lie'
    aliases = ['lie prone', 'lie down', 'prone']
    help_category = 'combat'

    def func(self):
        if not self.args:
            self.caller.msg("Usage: lie [prone]")
            return

        self.caller.ndb.combat_handler.add_action(
            action="lie",
            character=self.caller,
            target=self.caller,
            duration=0)

        self.caller.msg("You add 'lie prone' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdAttack(default_cmds.MuxCommand):
    """implementation melee and ranged attack shared functionality"""
    key = 'attack'
    aliases = []
    locks = 'cmd:holds()'
    help_category = 'combat'

    def func(self):
        attack_type = self.attack_type if hasattr(self, 'attack_type') \
                        else 'attack'
        duration = self.duration if hasattr(self, 'duration') else 1

        if not self.args:
            self.caller.msg("Usage: {}[/s] <target>".format(attack_type))
            return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        target = self.caller.search(
                    self.args,
                    candidates=self.caller.ndb.combat_handler.characters.values())

        if not target:
            return

        ok = self.caller.ndb.combat_handler.add_action(
                action="{}{}".format(attack_type, switch),
                character=self.caller,
                target=target,
                duration=duration)

        if ok:
            self.caller.msg(
                "You add '{attack}{switch} {target}' to the combat queue".format(
                    attack=attack_type,
                    switch=switch,
                    target=target.get_display_name(self.caller)))
        else:
            self.caller.mssg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


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

    aliases = ['stab', 'slice', 'chop', 'slash', 'bash']

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

    aliases = ['fire at', 'shoot']

    def func(self):
        super(CmdAttackMelee, self).func()


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
    help_category = 'combat'

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
    help_category = 'combat'

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
    help_category = 'combat'

    def func(self):

        self.caller.ndb.combat_handler.add_action(
            action="dodge",
            character=self.caller,
            target=self.caller,
            duration=1)

        self.caller.msg("You add 'dodge' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdAdvance(default_cmds.MuxCommand):
    """
    move toward an opponent

    Usage:
      advance [<target>]

    Moves your character from 'ranged' range to
    'melee' range with the specified opponent.

    This is a half-turn combat action.
    """
    key = 'advance'
    aliases = ['approach', 'adv', 'appr']
    help_category = 'combat'

    def func(self):
        combat_chars = self.caller.ndb.combat_handler.characters
        target = None
        if not self.args:
            if len(combat_chars) == 2:
                target = [x for x in combat_chars if x.id != self.caller.id][0]
            else:
                self.caller.msg("Usage: advance <target>")
                return

        target = target or self.caller.search(
                                self.args,
                                candidates=combat_chars.values())

        if not target:
            return

        self.caller.ndb.combat_handler.add_action(
            action="advance",
            character=self.caller,
            target=target,
            duration=1)

        self.caller.msg("You add 'advance' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdRetreat(default_cmds.MuxCommand):
    """
    move away from all opponents

    Usage:
      retreat [spaces]

    Args:
      spaces - number of spaces to move

    Attempts to moves your character away from all
    other combatants. If spaces is not specified, uses
    all available MV points.

    This is a half-turn combat action.
    """
    key = 'retreat'
    aliases = []
    help_category = 'combat'

    def func(self):

        self.caller.ndb.combat_handler.add_action(
            action="retreat",
            character=self.caller,
            target=self.caller,
            duration=1)

        self.caller.msg("You add 'retreat' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdStand(default_cmds.MuxCommand):
    """
    stand up from a prone position

    Usage:
      stand

    Removes the bonus and pentalty for lying prone,
    and allows your character to move.

    This is a half-turn combat action.
    """
    key = 'stand'
    aliases = ['get up', 'arise']
    help_category = 'combat'

    def func(self):

        self.caller.ndb.combat_handler.add_action(
            action="stand",
            character=self.caller,
            target=self.caller,
            duration=1)

        self.caller.msg("You add 'stand' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdGet(default_cmds.CmdGet):
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
    help_category = 'combat'

    def func(self):

        if not self.args:
            self.caller.msg("Usage: get <obj>")
            return

        target = self.caller.search(self.args)

        if not target:
            return

        self.caller.ndb.combat_handler.add_action(
            action="get",
            character=self.caller,
            target=target.get_display_name(self.caller),
            duration=1)

        self.caller.msg("You add 'get {}' to the combat queue".format(
            target.get_display_name(self.caller)))

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdEquip(EQUIP_CMD):
    """
    equip a weapon or piece of armor

    Usage:
      equip <item>

    Equips an item to its required slot(s).

    This is a half-turn combat action.
    """
    key = 'equip'
    aliases = ['wear', 'wield']
    help_category = 'combat'

    def func(self):

        if not self.args:
            self.caller.msg("Usage: equip <item>")
            return

        target = self.caller.search(self.args)

        if not target:
            return

        self.caller.ndb.combat_handler.add_action(
            action="equip",
            character=self.caller,
            target=target.get_display_name(self.caller),
            duration=1)

        self.caller.msg("You add 'equip {}' to the combat queue".format(
            target.get_display_name(self.caller)))

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


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
    help_category = 'combat'

    def func(self):
        if not self.args:
            self.caller.msg("Usage: wrestle[/break] <target>")
            return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        combat_chars = self.caller.ndb.combat_handler.characters.values()

        target = self.caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = self.caller.ndb.combat_handler.add_action(
                action="wrestle{}".format(switch),
                character=self.caller,
                target=target,
                duration=2)

        if ok:
            self.caller.msg(
                "You add 'wrestle{switch} {target}' to the combat queue".format(
                    switch=switch,
                    target=target.get_display_name(self.caller)))
        else:
            self.caller.mssg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


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
    help_category = 'combat'

    def func(self):
        if not self.args:
            self.caller.msg("Usage: tackle <target>")
            return

        combat_chars = self.caller.ndb.combat_handler.characters.values()

        target = self.caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = self.caller.ndb.combat_handler.add_action(
                action="tackle",
                character=self.caller,
                target=target,
                duration=3)

        if ok:
            self.caller.msg(
                "You add 'tackle {target}' to the combat queue".format(
                    target=target.get_display_name(self.caller)))
        else:
            self.caller.mssg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


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
    help_category = 'combat'

    def func(self):

        self.caller.ndb.combat_handler.add_action(
            action="flee",
            character=self.caller,
            target=self.caller,
            duration=2)

        self.caller.msg("You add 'flee' to the combat queue")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()
