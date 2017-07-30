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
            # `caller` is who is being asked the question
            # `prompt` is what to ask
            # `callback` is the function to call after the user decides
            # `map` is passed to the callback.
            get_input(caller=caller, prompt='Are you sure you want to wipe this map?', callback=really_wipe_map, map=theMap)
        else:
            caller.msg((theMap.return_appearance(self.caller), {"type": "map"}))

def really_wipe_map(caller, prompt, result, map):
    '''
    This gets called by CmdMap.

    caller: the player who decided to wipe the map
    prompt: (ignored)
    result: what the caller responded with
    map: the map to wipe
    '''
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
