"""
Death Module
"""
from math import floor
from evennia import CmdSet, Command
from evennia.utils import delay
from typeclasses.scripts import Script
from world.rulebook import d_roll


# Scripts


class DeathHandler(Script):
    """Base script for death mechanics handlers."""
    def at_script_creation(self):
        super(DeathHandler, self).at_script_creation()

        self.key = "death_handler_{}".format(self.obj.id)
        self.desc = "handles character death"
        self.interval = 0
        self.repeats = 0
        self.start_delay = False
        self.persistent = True

        self.db.death_step = 0
        self.db.death_cb = None
        # subclasses define the sequence of callbacks
        self.db.death_sequence = ()

    def at_start(self):
        """Parent at_start should be called first in subclasses."""
        self.obj.cmdset.add(DeadCmdSet)
        if len(self.db.death_sequence) > 0 and self.db.death_step > 0:
            delay(3, getattr(self, self.db.death_sequence[self.db.death_step]))

    def at_stop(self):
        self.obj.cmdset.remove(DeadCmdSet)


class CharDeathHandler(DeathHandler):
    """Script that handles death mechanics for Characters."""
    def at_script_creation(self):
        super(CharDeathHandler, self).at_script_creation()
        self.db.death_sequence = \
            ('floating', 'returning', 'pre_revive', 'revive')

    def at_start(self):
        """Handles the 'phases' of death"""
        super(CharDeathHandler, self).at_start()
        self.obj.msg("You have died.")
        self.obj.location.msg_contents("{character} falls dead.",
                                       mapping={'character': self.obj},
                                       exclude=self.obj)

        self.obj.db.pose = self.obj.db.pose_death
        self.obj.traits.XP.base = int(floor(0.1 * self.obj.traits.XP.actual))
        delay(20, getattr(self, self.db.death_sequence[self.db.death_step]))

    def floating(self):
        self.obj.msg("Your awareness blinks back into existence briefly. You float in the aethers.")
        # remove the body
        self.obj.location.msg_contents("The body of {character} rots away to dust.",
                                       mapping={'character': self.obj},
                                       exclude=self.obj)
        limbo = self.obj.search('Limbo', global_search=True)
        self.obj.move_to(limbo, quiet=True, move_hooks=False)
        self.db.death_step += 1
        delay(8, getattr(self, self.db.death_sequence[self.db.death_step]))

    def returning(self):
        self.obj.msg(
            "You feel a quickening in your energy as you feel pulled back toward |mAinneve|n.")
        self.obj.home.msg_contents(
            "A sudden roar fills the chamber as the fire grows tall and the surface |/"
            "of the purple pool becomes agitated, spattering droplets into the air |/"
            "surrounding the flame.")
        self.db.death_step += 1
        delay(3, getattr(self, self.db.death_sequence[self.db.death_step]))

    def pre_revive(self):
        self.obj.msg(
            "A blinding light flashes before you and you feel your body lurch forward onto |/"
            "a smooth stone floor. Your ears ring from the deafening sound of your return.")
        self.obj.home.msg_contents(
            "More and more purple droplets arise in a column around the flame which roars|/"
            "ever brighter. Without warning, the column erupts in a blinding flash of light.|/"
            "When your sight returns, the figure of {character} stands at the center of the|/"
            "shrine looking confused.",
            mapping=dict(character=self.obj),
            exclude=self.obj)
        self.db.death_step += 1
        delay(3, getattr(self, self.db.death_sequence[self.db.death_step]))

    def revive(self):
        # revive the dead character
        self.obj.traits.HP.fill_gauge()
        self.obj.traits.SP.fill_gauge()
        self.obj.db.pose = self.obj.db.pose_default
        self.obj.move_to(self.obj.home, quiet=True)
        self.stop()


class NPCDeathHandler(DeathHandler):
    """Script that handles death mechanics for NPCs."""
    def at_script_creation(self):
        super(NPCDeathHandler, self).at_script_creation()
        self.db.death_sequence = ('storage', 'revive')

    def at_start(self):
        """Handles the 'phases' of death"""
        super(NPCDeathHandler, self).at_start()
        self.obj.location.msg_contents("{character} falls dead.",
                                       mapping={'character': self.obj},
                                       exclude=self.obj)

        self.obj.db.pose = self.obj.db.pose_death
        delay(10 * d_roll('1d6'),
              getattr(self, self.db.death_sequence[self.db.death_step]))

    def storage(self):
        # remove the body
        self.obj.location.msg_contents("The body of {npc} rots away to dust.",
                                       mapping={'npc': self.obj},
                                       exclude=self.obj)
        limbo = self.obj.search('Limbo', global_search=True)
        self.obj.move_to(limbo, quiet=True, move_hooks=False)
        self.db.death_step += 1
        delay(10 * d_roll('1d12') + 30,
              getattr(self, self.db.death_sequence[self.db.death_step]))

    def revive(self):
        # revive the dead NPC
        self.obj.traits.HP.fill_gauge()
        self.obj.traits.SP.fill_gauge()
        self.obj.db.pose = self.obj.db.pose_default
        self.obj.move_to(self.obj.home)
        self.stop()


# Commands


class DeadCmdSet(CmdSet):

    key = "death_cmdset"
    mergetype = "Replace"
    priority = 100
    no_exits = True
    no_objs = True

    def at_cmdset_creation(self):
        self.add(CmdDeadHelp())


class CmdDeadHelp(Command):
    """Help command when dead."""

    key = 'help'

    def func(self):
        self.caller.msg('|rY O U   A R E   D E A D|n')
        self.caller.msg(
            "You're dead. What more is there to say? Why don't you kick back |/"
            "and enjoy having no responsibilities for once?"
        )
