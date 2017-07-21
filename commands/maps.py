# -*- coding: utf-8 -*-

"""
Building commands
"""

from .command import MuxCommand
from evennia import utils, CmdSet
from evennia.utils.evtable import EvTable


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
    view a held map

    Usage
      map
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
        caller.msg((theMap.return_appearance(self.caller), {"type": "map"}))
