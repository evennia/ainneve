"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""
from django.conf import settings
from evennia.contrib.grid.xyzgrid.launchcmd import xyzcommand
from evennia.contrib.grid.xyzgrid.xyzgrid import get_xyzgrid

def at_initial_setup():
    maps_list = settings.XYZGRID_MAP_LIST
    xyzcommand("add",*maps_list)

    grid = get_xyzgrid()

    # override grid's logger to echo directly to console
    def _log(msg):
        print(msg)

    grid.log = _log
    grid.spawn(xyz=("*", "*", "*"))
