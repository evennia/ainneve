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

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# SERVERNAME = "Your Game Name Here"
#
# Can actually be in secret_settings.py instead, so as not to
# collide with other games on the Evennia Game Index website

# Server ports. If enabled and marked as "visible", the port
# should be visible to the outside world on a production server.
# NOTE:   there are many more options available beyond these.
#         These settings are "default" for Ainneve.com in 2022,
#         running on a server configured with secure haproxy.
#         For details:
# https://www.evennia.com/docs/1.0-dev/Setup/HAProxy-Config.html
#

IRC_ENABLED = False
IDLE_TIMEOUT = 86400

# Telnet ports. Visible to the world
TELNET_ENABLED = True
TELNET_INTERFACES = ["0.0.0.0"]

# Force Webserver and Websockets to use localhost
# Haproxy will use the server's external IP and
# forward into the standard 4001/4002 ports
WEBSERVER_ENABLED = True
WEBSERVER_INTERFACES = ["127.0.0.1"]

WEBSOCKET_CLIENT_URL = "wss://ainneve.com:4002/"
WEBSOCKET_CLIENT_INTERFACE = "127.0.0.1"


######################################################################
# Django web features
######################################################################

# Allow multiple sessions per account; one character per session
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

BASE_BATCHPROCESS_PATHS = ['.world.content']


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print ("secret_settings.py file not found or failed to import.")

try:
    # Created by the `evennia connections` wizard
    from .connection_settings import *
except ImportError:
    pass
