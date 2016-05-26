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

# Other defaults
PROTOTYPE_MODULES = ('world.content.prototypes_armor',
                     'world.content.prototypes_items',
                     'world.content.prototypes_misc',
                     'world.content.prototypes_mobs',
                     'world.content.prototypes_weapons'
                     )
BASE_BATCHPROCESS_PATHS = ['world.build']

