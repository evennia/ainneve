
import random
from .scripts import Script
from world.rulebook import resolve_combat
from evennia import TICKER_HANDLER as tickerhandler

class CombatHandler(Script):
    """
    This implements the combat handler.
    """

    # standard Script hooks

    def at_script_creation(self):
        "Called when script is first created"

        self.key = "combat_handler_%i" % random.randint(1, 1000)
        self.desc = "handles combat"
        self.interval = 60 * 2  # two minute timeout
        self.start_delay = True
        self.persistent = True

        # store all combatants
        self.db.characters = {}
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
        character.ndb.combat_handler = self
        character.cmdset.add("commands.combat.CombatCmdSet")
        tickerhandler.remove(6, character.at_turn_start)

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
        del character.ndb.combat_handler
        character.cmdset.delete("commands.combat.CombatCmdSet")
        tickerhandler.add(6, character.at_turn_start)

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
        for character in list(self.db.characters.values()):
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
        self.db.characters[dbref] = character
        self.db.action_count[dbref] = 0
        self.db.turn_actions[dbref] = []
        self.db.pending_actions[dbref] = []
        # set up back-reference
        self._init_character(character)

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

    def add_action(self, action, character, target, duration):
        """
        Called by combat commands to register an action with the handler.

         action - string identifying the action, like "hit" or "parry"
         character - the character performing the action
         target - the target character or None

        actions are stored in a dictionary keyed to each character, each
        of which holds a list of max 2 actions. An action is stored as
        a tuple (character, action, target).
        """
        dbref = character.id
        count = self.db.action_count[dbref]
        if 0 <= count <= 1:  # only allow 2 duration worth of actions
            self.db.turn_actions[dbref].append((action, character, target, duration))
        else:
            # report if we already used too many actions
            return False
        self.db.action_count[dbref] = sum([x[3] for x in self.db.turn_actions[dbref]])
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
        is called by at_repeat(). The 'resolve_combat' function
        populates pending_actions with any actions that were
        not completed in this turn.
        """
        resolve_combat(self, self.db.turn_actions)

        if len(self.db.characters) < 2:
            # if we have less than 2 characters in battle, kill this handler
            self.msg_all("Combat has ended")
            self.stop()
        else:
            # reset counters before next turn
            for character in self.db.characters.values():
                self.db.characters[character.id] = character
                self.db.turn_actions[character.id] = self.db.pending_actions[character.id] or []
                self.db.action_count[character.id] = sum([x[3] for x in self.db.turn_actions[character.id]])
                self.db.pending_actions[character.id] = []
                character.at_turn_start()
            self.msg_all("Next turn begins ...")
