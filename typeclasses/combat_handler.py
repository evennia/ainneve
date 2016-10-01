
from collections import deque, OrderedDict
from operator import add
import random
from .scripts import Script
from evennia import TICKER_HANDLER as tickerhandler
from evennia.utils import utils, make_iter


COMBAT_DISTANCES = ['melee', 'reach', 'ranged']
WRESTLING_POSITIONS = ('STANDING', 'CLINCHED', 'TAKE DOWN', 'PINNED')

_ACTIONS_PER_TURN = utils.variable_from_module('world.rulebook', 'ACTIONS_PER_TURN')
_COMBAT_PROMPT = ("|M[|n HP: |g{tr.HP.actual}|n "
                  "|| WM: |w{tr.WM.actual}|n "
                  "|| BM: |x{tr.BM.actual}|n "
                  "|| SP: |y{tr.SP.actual}|n |M]|n")


class CombatHandler(Script):
    """
    This implements the combat handler.
    """

    # standard Script hooks

    def at_script_creation(self):
        "Called when script is first created"

        self.key = "combat_handler_%i" % random.randint(1, 1000)
        self.desc = "handles combat"
        self.interval = 15  # two minute timeout
        self.start_delay = True
        self.persistent = True

        # store all combatants
        self.db.characters = {}
        # distance between combatants
        self.db.distances = {}
        # store all actions for each turn
        self.db.turn_actions = {}
        # number of actions entered per combatant
        self.db.action_count = {}

    def _init_character(self, character):
        """
        This initializes handler back-reference
        and combat cmdset on a character. It also
        stops the tickerhandler that normally calls
        at_turn_start every 6s
        """
        if not character.nattributes.has('combat_handler'):
            tickerhandler.remove(6, character.at_turn_start)
            character.ndb.combat_handler = self
            character.cmdset.add("commands.combat.CombatBaseCmdSet")
            character.cmdset.add("commands.combat.CombatCmdSet")
            prompt = _COMBAT_PROMPT.format(tr=character.traits)
            character.msg(prompt=prompt)

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset. Also
        re-starts the tickerhandler
        """
        dbref = character.id
        del self.db.characters[dbref]
        del self.db.turn_actions[dbref]
        del self.db.action_count[dbref]
        for key in [k for k in self.db.distances.keys()
                    if dbref in k]:
            del self.db.distances[key]

        character.at_turn_end()
        del character.ndb.combat_handler
        if character.cmdset.has_cmdset("combat_cmdset"):
            character.cmdset.remove("commands.combat.CombatCmdSet")
        character.cmdset.remove("commands.combat.CombatBaseCmdSet")
        tickerhandler.add(6, character.at_turn_start)
        character.msg(prompt=' ')

    def at_start(self):
        """
        This is called on first start but also when the script is restarted
        after a server reboot. We need to re-assign this combat handler to
        all characters as well as re-assign the cmdset.
        """
        for character in self.db.characters.values():
            self._init_character(character)

    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        for character in self.db.characters.values():
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)

    def at_repeat(self, *args):
        """
        This is called every self.interval seconds or when force_repeat
        is called (because everyone has entered their commands).

        We let this method take optional arguments (using *args) so we can separate
        between the timeout (no argument) and the controlled turn-end
        where we send an argument.
        """
        if not args:
            self.msg_all("Turn timer timed out. Continuing.")
        self.end_turn()

    # Combat-handler methods

    def add_character(self, character):
        "Add combatant to handler"
        dbref = character.id
        for cid in self.db.characters.keys():
            # all characters start at 'ranged' distance from each other
            self.db.distances[frozenset((cid, character.id))] = 'ranged'

        self.db.characters[dbref] = character
        self.db.action_count[dbref] = 0
        self.db.turn_actions[dbref] = deque([])
        # set up back-reference
        self._init_character(character)
        character.at_turn_start()

    def remove_character(self, character):
        "Remove combatant from handler"
        if character.id in self.db.characters:
            self._cleanup_character(character)

        if not self.db.characters:
            # if we have no more characters in battle, kill this handler
            self.stop()
 
    def msg_all(self, message, exclude=()):
        "Send message to all combatants"
        for character in self.db.characters.values():
            if character not in exclude:
                character.msg(message)

    def combat_msg(self, messages, actor, target=None, exclude=None, **kwargs):
        """Sends messaging to combat participants and vicinity.

        Args:
          messages (tuple): tuple of messages with up to three items:
              1. a message sent to the actor
              2. a message sent to the actor's location
              3. an message sent to the target (optional)

          actor (Character): the character taking the action, keyed
                in messages as {actor}.
          target (Character, optional): the character or object being
                targeted in the action, keyed in messages as {target}.
          kwargs: any other format substitution keys should be passed
                in as kwargs.

        Example:
            ch.combat_msg(("You attack {target} with {weapon}.",
                           "{actor} attacks {target} with {weapon}.",
                           "{actor} attacks you with {weapon}."),
                          actor=attacker,
                          target=defender,
                          weapon=weapon)
        """
        exclude = make_iter(exclude) if exclude else []
        exclude.append(actor)

        # actor messaging
        mapping = {t: sub.get_display_name(actor)
                   if hasattr(sub, 'get_display_name')
                   else str(sub)
                   for t, sub in kwargs.items()}
        if target:
            exclude.append(target)
            mapping.update({'target': target.get_display_name(actor)
                            if hasattr(target, 'get_display_name')
                            else str(target)})

        actor.msg(messages[0].format(**mapping),
                  prompt=_COMBAT_PROMPT.format(tr=actor.traits))

        # room messaging
        mapping = {t: sub for t, sub in kwargs.items()}
        mapping.update({'actor': actor, 'target': target})
        actor.location.msg_contents(messages[1],
                                    mapping=mapping,
                                    exclude=exclude)

        # target messaging
        if target:
            mapping = {t: sub.get_display_name(target)
                       if hasattr(sub, 'get_display_name')
                       else str(sub)
                       for t, sub in kwargs.items()}
            mapping['actor'] = actor.get_display_name(target)
            target.msg(messages[2].format(**mapping),
                       prompt=_COMBAT_PROMPT.format(tr=target.traits))

    def add_action(self, action, character, target, duration, longturn=False):
        """
        Called by combat commands to register an action with the handler.

         action - string identifying the action, like "hit" or "parry"
         character - the character performing the action
         target - the target character or None
         duration - the duration of the action

        actions are stored in a dictionary keyed to each character, each
        of which holds a list of actions. An action is stored as
        a tuple (action, character, target, duration).
        """
        dbref = character.id
        count = self.db.action_count[dbref]
        if 0 <= count < _ACTIONS_PER_TURN or longturn:
            self.db.turn_actions[dbref].append((action, character, target, duration))
        else:
            # report if we already used too many actions
            return False
        self.db.action_count[dbref] = \
            sum([x[3] for x in self.db.turn_actions[dbref]])
        return True

    def remove_last_action(self, character):
        """Removes the last action in the queue for specified character.

        Returns:
            Either a tuple containing the action and target removed,
            or a tuple containing (False, False)
        """
        dbref = character.id

        if len(self.db.turn_actions[dbref]) == 0:
            return False, False
        else:
            action, _, target, _ = self.db.turn_actions[dbref].pop()
            self.db.action_count[dbref] = \
                sum([x[3] for x in self.db.turn_actions[dbref]])
            return action, target

    def get_range(self, character, target):
        """Returns the range for a pair of combatants."""
        return self.db.distances[frozenset((character.id, target.id))]

    def get_min_range(self, character, max=False):
        """Returns the name of the nearest range wth opponents.

        Args:
          character (Character): character object to center on
          max (boolean): if true, return the farthest range
                         containing opponents
            """
        char_prox = self.get_proximity(character)
        for rng in char_prox:
            if len(char_prox[rng]) > 0:
                return rng
        return None

    def get_proximity(self, character):
        """Returns a list of lists of character dbrefs by distance."""
        proximities = OrderedDict()
        for rng in COMBAT_DISTANCES:
            proximities[rng] = []

        if character:
            for id, rng in [(next(iter(k.difference(frozenset((character.id,))))), r)
                            for k, r in self.db.distances.items()
                            if character.id in k]:
                proximities[rng].append(id)

        return proximities

    def move_character(self, character, to_range, from_range, target=None):
        """Changes a character's range with respect to one or more other combatants."""
        _CD = COMBAT_DISTANCES
        distances = self.db.distances
        char_prox = self.get_proximity(character)
        targ_prox = self.get_proximity(target)

        if target:
            # advancing; set the distance between the character and target
            distances[frozenset((character.id, target.id))] = to_range

            if to_range == 'melee':
                # char takes on target's distances for all others
                for rng in _CD:
                    for cid in targ_prox[rng]:
                        if cid != character.id:
                            distances[frozenset((character.id, cid))] = rng

        else:  # retreating; to_range is either 'reach' or 'ranged'
            from world.rulebook import skill_check
            # have to pass a balance skill test to retreat from melee
            ok = True
            if from_range == 'melee':
                ok = skill_check(character.skills.balance.actual, 4) and \
                     _CD.index(to_range) > _CD.index(from_range)
            if ok:
                for cid in reduce(add, [char_prox[rng] for rng
                                        in _CD[:_CD.index(to_range)]]):
                    distances[frozenset((character.id, cid))] = to_range
        return True

    def check_end_turn(self):
        """
        Called by the command to eventually trigger
        the resolution of the turn. We check if everyone
        has added all their actions; if so we call self.end_turn()
        """
        if all(count > 1 for count in self.db.action_count.values()):
            # this will both reset timer and trigger self.end_turn()
            self.at_repeat("endturn")

    def end_turn(self):
        """
        This resolves all actions by calling the rules module.
        It then resets everything and starts the next turn. It
        is called by at_repeat().
        """
        self.pause()

        for character in self.db.characters.values():
            character.cmdset.remove("commands.combat.CombatCmdSet")
            character.at_turn_end()

        from world.rulebook import resolve_combat
        resolve_combat(self)

    def begin_turn(self):
        if len(self.db.characters) < 2:
            # if we have less than 2 characters in battle, kill this handler
            self.msg_all("Combat has ended")
            for character in self.db.characters.values():
                self._cleanup_character(character)
            self.stop()
        else:
            # reset counters before next turn
            for character in self.db.characters.values():
                self.db.characters[character.id] = character
                self.db.action_count[character.id] = \
                    sum([x[3] for x in self.db.turn_actions[character.id]])
                character.at_turn_start()
                character.cmdset.add("commands.combat.CombatCmdSet")

            self.msg_all("Next turn begins. Declare your actions!")
            self.unpause()
