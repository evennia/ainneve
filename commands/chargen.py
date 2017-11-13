"""
Chargen commands.

Ainneve implements MULTISESSION_MODE = 2, in which accounts enter an
OOC state immediately after creation. From that state, the @charcreate
command is available to create a new character. This command launches
the Ainneve character creation EvMenu.

This new @charcreate command is added to the session cmdset. We also
create a cmdset with the "Remove" mergetype to remove the original
version from the account cmdset.

To ensure that accounts cannot puppet a character until it has completed
the entire character creation process, we also override the default @ic
command on the account.
"""
from django.conf import settings
from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxAccountCommand
from evennia import default_cmds
from evennia.utils import create, search
from evennia.utils.evmenu import EvMenu
from world.archetypes import validate_primary_traits

_MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
_MULTISESSION_MODE = settings.MULTISESSION_MODE


class CharCreateCmdSet(CmdSet):
    """Command set to add @charcreate command to Session."""
    key = "chargen_cmdset"
    priority = 0

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdCharCreate())


class RemoveCharCreateCmdSet(CmdSet):
    """Command set to remove @charcreate command from Account."""
    key = "rem_charcreate_cmdset"
    priority = 2
    mergetype = "Remove"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdCharCreate())


class ChargenICCmdSet(CmdSet):
    """Command set to override the @ic command on Account"""
    key = 'chargen_ic_cmdset'
    priority = 2

    def at_cmdset_creation(self):
        self.add(CmdIC())


class CmdIC(default_cmds.CmdIC):
    """
    control an object you have permission to puppet

    Usage:
      @ic <character>

    Go in-character (IC) as a given Character.

    This will attempt to "become" a different object assuming you have
    the right to do so. Note that it's the ACCOUNT that puppets
    characters/objects and which needs to have the correct permission!

    You cannot become an object that is already controlled by another
    account. In principle <character> can be any in-game object as long
    as you the account have access right to puppet it.
    """
    def func(self):
        """Don't allow puppeting unless the chargen_complete attribute is set."""
        if self.args:
            new_character = search.object_search(self.args)
            if new_character:
                new_character = new_character[0]
                if (new_character.is_typeclass('typeclasses.characters.Character') and
                        not new_character.db.chargen_complete):
                    self.session.execute_cmd('@charcreate {}'.format(
                        new_character.key
                    ))
                    return
            else:
                self.msg("That is not a valid character choice.")
                return
        super(CmdIC, self).func()


class CmdCharCreate(MuxAccountCommand):
    """
    create a new character

    Usage:
      @charcreate <charname>

    Create a new character. You may use upper-case letters in the
    name - you will nevertheless always be able to access your
    character using lower-case letters if you want.
    """
    key = "@charcreate"
    locks = "cmd:pperm(Player)"
    help_category = "General"

    def func(self):
        "create the new character"
        account = self.account
        session = self.session
        if not self.args:
            self.msg("Usage: @charcreate <charname>")
            return
        key = self.args.strip()

        charmax = _MAX_NR_CHARACTERS if _MULTISESSION_MODE > 1 else 1

        if not account.is_superuser and \
            (account.db._playable_characters and
                len(account.db._playable_characters) >= charmax):
            self.msg(
                "You may only create a maximum of {} characters.".format(
                    charmax))
            return

        # create the character
        from evennia.objects.models import ObjectDB

        start_location = search.objects('Kai River Bridge')
        start_location = start_location[0] if start_location \
            else ObjectDB.objects.get_id(settings.START_LOCATION)

        home = search.objects('Shrine of Grass')
        home = home[0] if home \
            else ObjectDB.objects.get_id(settings.DEFAULT_HOME)

        typeclass = settings.BASE_CHARACTER_TYPECLASS
        permissions = settings.PERMISSION_ACCOUNT_DEFAULT

        # check whether a character already exists
        new_character = None
        candidates = search.objects(
            key,
            typeclass='typeclasses.characters.Character')

        if candidates:
            for c in candidates:
                if c.access(account, 'puppet'):
                    new_character = c
                    break

        startnode = "menunode_welcome_archetypes"
        if not new_character:

            new_character = create.create_object(typeclass, key=key,
                                                 location=None,
                                                 home=home,
                                                 permissions=permissions)
            # only allow creator (and immortals) to puppet this char
            new_character.locks.add(
                ("puppet:id({}) or pid({}) "
                 "or perm(Immortals) or pperm(Immortals)").format(
                    new_character.id, account.id
                ))
            account.db._playable_characters.append(new_character)

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
                if (new_character.db.focus or (not new_character.db.focus
                         and validate_primary_traits(new_character.traits)[0])):
                    startnode = "menunode_races"
                    if new_character.db.race:
                        startnode = "menunode_allocate_mana"
                        if (new_character.traits.BM.base + new_character.traits.WM.base
                                == new_character.traits.MAG.actual
                                and len(new_character.skills.all) > 0):
                            startnode = "menunode_allocate_skills"
                            if ('escape' in new_character.skills.all
                                and not hasattr(new_character.skills.escape, 'minus')):
                                startnode = "menunode_equipment_cats"

        session.new_char = new_character

        def finish_char_callback(session, menu):
            char = session.new_char
            if char.db.chargen_complete:
                char.location = start_location
                account.puppet_object(session, char)
                char.execute_cmd("help getting started")

        EvMenu(session,
               "world.chargen",
               startnode=startnode,
               cmd_on_exit=finish_char_callback)
