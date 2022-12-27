"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit
from evennia.contrib.grid import wilderness
from world.overworld import Overworld
from world.overworld.landmarks import OverworldLandmarks

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_post_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """

    pass

class OverworldExit(wilderness.WildernessExit):
    def at_traverse_coordinates(self, traversing_object, current_coordinates, new_coordinates):
        """
        Called when an object wants to travel from one place inside the
        wilderness to another place inside the wilderness.

        If this returns True, then the traversing can happen. Otherwise it will
        be blocked.

        This method is similar how the `at_traverse` works on normal exits.

        Args:
            traversing_object (Object): The object doing the travelling.
            current_coordinates (tuple): (x, y) coordinates where
                `traversing_object` currently is.
            new_coordinates (tuple): (x, y) coordinates of where
                `traversing_object` wants to travel to.

        Returns:
            bool: True if traversing_object is allowed to traverse
        """
        if not self.mapprovider.is_valid_coordinates(self.wilderness, new_coordinates):
            return False
        return True


class OverworldEntrance(Exit):
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This overrides default traversal to instead 'move' into the Overworld

        Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        source_location = traversing_object.location
        area_id = source_location.tags.get(category='area_id')
        landmark = OverworldLandmarks.get(area_id)

        if Overworld.enter(traversing_object, coordinates=landmark.coordinates):
            self.at_post_traverse(traversing_object, source_location)
            traversing_object.execute_cmd('look')
        else:
            self.at_failed_traverse(traversing_object)
