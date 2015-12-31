
riverport_1 = {"key": "Gate Street Bridge",
               "aliases": "riverport_1",
               "typeclass": "typeclasses.rooms.Room", # the path is automatically constructed using TYPECLASS_PATHS from evennia.settings_default.py
               "desc": '''The bridge on Gate Street connects the Council Quarter to the east with the Market Quarter to the west.''',
               }

riverport_1_east = {"key": "east",
                    "typeclass": "typeclasses.exits.Exit",
                    "location": "riverport_1",
                    "destination": "riverport_3",
                    }

riverport_2 = {"key": "Gate Street",
               "aliases": "riverport_2",
               "typeclass": "typeclasses.rooms.Room",
               "desc": '''The street goes here through the Market Quarter with the bridge directly to the east and the western gate in the distance.''',
               }

riverport_3 = {"key": "Gate Street",
               "aliases": "riverport_3",
               "typeclass": "typeclasses.rooms.Room",
               "desc": '''The street goes here through the Council Quarter with the bridge directly to the west and the eastern gate in the distance.''',
               }

