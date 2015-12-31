#HEADER

from evennia.utils.spawner import spawn
from evennia.utils.utils import dbref
from evennia.objects.models import ObjectDB

from world.content.riverport import objects

alias_to_obj = ObjectDB.objects.get_objs_with_key_or_alias

game_objs = []
for k, v in objects.__dict__.iteritems(): # TODO Python 3 compatibility
    if not k.startswith("_"):
        game_objs.append(v)


#CODE (create rooms)

for x in game_objs:
    if not "exit" in x["typeclass"]:
        spawn(x)


#CODE (create exits)
from pprint import pprint
for x in game_objs:
    if "exit" in x["typeclass"]:
        # convert string aliases to objects now that all the rooms are created, note that alias_to_obj returns a list
        print "before changes..."
        pprint(x)
        x["location"] = alias_to_obj(x["location"])[0]
        x["destination"] = alias_to_obj(x["destination"])[0]
        print "after changes..."
        pprint(x)
        spawn(x)