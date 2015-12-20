"""
Chargen commands.
"""
from django.conf import settings
from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxPlayerCommand
from evennia.utils import create, search
from evennia.utils.evmenu import EvMenu
from world.archetypes import validate_primary_traits

_MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
_MULTISESSION_MODE = settings.MULTISESSION_MODE


class ChargenCmdSet(CmdSet):
    """Command set for the 'chargen' command."""
    key = "chargen_cmdset"
    priority = 0

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdCharCreate())


class PlayerChargenCmdSet(CmdSet):
    """Command set to remove the @charcreate command from Player."""
    key = "chargen_cmdset"
    priority = 2
    mergetype = "Remove"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdCharCreate())


class CmdCharCreate(MuxPlayerCommand):
    """
    create a new character

    Usage:
      @charcreate <charname>

    Create a new character. You may use upper-case letters in the
    name - you will nevertheless always be able to access your
    character using lower-case letters if you want.
    """
    key = "@charcreate"
    locks = "cmd:pperm(Players)"
    help_category = "General"

    def func(self):
        "create the new character"
        player = self.player
        session = self.session
        if not self.args:
            self.msg("Usage: @charcreate <charname>")
            return
        key = self.args.strip()

        charmax = _MAX_NR_CHARACTERS if _MULTISESSION_MODE > 1 else 1

        if not player.is_superuser and \
            (player.db._playable_characters and
                len(player.db._playable_characters) >= charmax):
            self.msg("You may only create a maximum of %i characters." % charmax)
            return

        # create the character
        from evennia.objects.models import ObjectDB

        start_location = ObjectDB.objects.get_id(settings.START_LOCATION)
        default_home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        permissions = settings.PERMISSION_PLAYER_DEFAULT

        # check whether a character already exists
        new_character = None
        candidates = search.objects(key, typeclass='typeclasses.characters.Character')
        if candidates:
            for c in candidates:
                if c.access(player, 'puppet'):
                    new_character = c
                    break

        startnode = "menunode_welcome_archetypes"
        if not new_character:

            new_character = create.create_object(typeclass, key=key,
                                                 location=None,
                                                 home=default_home,
                                                 permissions=permissions)
            # only allow creator (and immortals) to puppet this char
            new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                    (new_character.id, player.id))
            player.db._playable_characters.append(new_character)

        else:
            if new_character.db.chargen_complete:
                self.msg(("{name} has already completed character "
                          "generation. Use @ic {name} to puppet.").format(
                            name=new_character.key
                                 if ' ' not in new_character.key
                                 else '"{}"'.format(new_character.key)))
                return
            if new_character.db.archetype:
                startnode = "menunode_allocate_traits"
                if validate_primary_traits(new_character.traits)[0]:
                    startnode = "menunode_races"
                if new_character.db.race:
                    startnode = "menunode_allocate_mana"
                if (new_character.traits.BM.base + new_character.traits.WM.base
                        == new_character.traits.MAG.actual):
                    startnode = "menunode_allocate_skills"
                if ('escape' in new_character.skills.all
                    and not hasattr(new_character.skills.escape, 'minus')):
                    startnode = "menunode_equipment_cats"

        session.new_char = new_character

        def finish_char_callback(session, menu):
            char = session.new_char
            if char.db.chargen_complete:
                char.location = start_location
                player.puppet_object(session, char)

        EvMenu(session,
               "typeclasses.chargen",
               startnode=startnode,
               allow_quit=True,
               cmd_on_quit=finish_char_callback)


class CmdCreateInventory(MuxPlayerCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows the inventory of the character currently being created.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        if hasattr(self.session, 'new_char'):
            session = self.session
            char = session.new_char
            old_msg = char.msg
            char.msg = session.msg
            char.execute_cmd('inventory')
            char.msg = old_msg

