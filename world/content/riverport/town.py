from evennia.objects.models import ObjectDB

_get_with_alias = ObjectDB.objects.get_objs_with_key_or_alias

RIVERPORT_1 = {"key": "Gate Street Bridge",
               "aliases": "riverport_1",
               "typeclass": "extended_room.ExtendedRoom", # the path is automatically constructed using TYPECLASS_PATHS from evennia.settings_default.py
               "general_desc": '''The bridge on Gate Street connects the Council Quarter to the east with the Market Quarter to the west.''',
               }

RIVERPORT_1_east = {"key": "east",
                    "typeclass": "exits.Exit",
                    "location": _get_with_alias("riverport_1"),
                    "destination": _get_with_alias("riverport_3"),
                    }

RIVERPORT_2 = {"key": "Gate Street",
               "aliases": "riverport_2",
               "typeclass": "extended_room.ExtendedRoom",
               "general_desc": '''The street goes here through the Market Quarter with the bridge directly to the east and the western gate in the distance.''',
               }

RIVERPORT_3 = {"key": "Gate Street",
               "aliases": "riverport_3",
               "typeclass": "extended_room.ExtendedRoom",
               "general_desc": '''The street goes here through the Council Quarter with the bridge directly to the west and the eastern gate in the distance.''',
               }

