# -*- coding: utf-8 -*-

"""
Building commands
"""

from .command import MuxCommand
from evennia import CmdSet
from evennia.utils.evmenu import get_input


class MapCmdSet(CmdSet):
    """
    Adds a `map` command to show the map.
    """
    key = "AinneveMap"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"
        self.add(CmdMap())

class CmdMap(MuxCommand):
    """
    View a held map

    Usage
      map - view the map
      map/reset - erase the contents of the map and start over with a blank map
    """

    key = "map"
    aliases = ["mpa"]
    help_category = "General"

    def func(self):
        caller = self.caller
        maps = caller.search('map', quiet=True)
        if len(maps) == 0:
            caller.msg('You don’t have any maps :(')
            return
        theMap = maps[0]
        if 'reset' in self.switches:
            get_input(caller, 'Are you sure you want to wipe this map?', really_wipe_map, None, theMap)
        else:
            caller.msg((theMap.return_appearance(self.caller), {"type": "map"}))

def really_wipe_map(caller, prompt, result, theMap):
    if result.lower() in ("y", "yes"):
        theMap.db.map_data = {}
        theMap.db.x = theMap.db.y = 0
        theMap.map_current_room()
    if result.lower() in ("n", "no"):
        return # don’t wipe the map
    else:
        # the answer is not on the right yes/no form
        caller.msg("Please answer Yes or No. \n%s" % prompt)
        # returning True will make sure the prompt state is not exited
        return True
