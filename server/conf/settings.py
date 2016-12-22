"""
Evennia settings file.
The available options are found in the default settings file found
here:
{settings_default}
Remember:
Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.
When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).
"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Ainneve"

IRC_ENABLED = True
IDLE_TIMEOUT = 86400

######################################################################
# Django web features
######################################################################


# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = '5(r:%@Gmg-?}NU3d[/ul8+t.SJ$",c`|qxsDo"Z='

# Allow multiple sessions per player; one character per session
MULTISESSION_MODE = 2
MAX_NR_CHARACTERS = 5
IRC_ENABLED = True

# Other defaults
PROTOTYPE_MODULES = ('world.content.prototypes_armor',
                     'world.content.prototypes_items',
                     'world.content.prototypes_misc',
                     'world.content.prototypes_mobs',
                     'world.content.prototypes_weapons'
                     )

BASE_BATCHPROCESS_PATHS = ['world.content']

# Evennia game index settings
GAME_INDEX_LISTING = {
    'game_status': 'pre-alpha',
    # Optional, comment out or remove if N/A
    'game_website': 'http://ainneve.evennia.com',
    'short_description': 'This is the example game for Evennia.',
    # Optional but highly recommended. Markdown is supported.
    'long_description': (
        "Launched in the summer of 2015 by the Evennia community, this project "
        "aims to be a full example implementation of a MUD-style RP-focused game.\n\n"
        "It is based on the [Open Adventure](https://github.com/openadventure/Open-Adventure/blob/master/rulebook/biem/openadventure_basic.pdf) "
        "table-top game system, is fantasy-themed, and features turn-based combat.\n\n"
        "It still a work in progress, and basic game systems are still being built. "
        "However, we welcome any who are interested in testing things out and giving "
        "feedback."
    ),
    'listing_contact': 'fened78@gmail.com',
    # At minimum, specify this or the web_client_url options. Both is fine, too.
    'telnet_hostname': 'ainneve.evennia.com',
    'telnet_port': 4000,
    # At minimum, specify this or the telnet_* options. Both is fine, too.
    'web_client_url': 'http://ainneve.evennia.com:8000/webclient',
}
