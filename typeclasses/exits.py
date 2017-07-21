"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit, utils

from maps import Map

class Exit(DefaultExit):
    """In Ainneve, Exits implement OA movement cost rules.

    All Rooms have a terrain type which determines movement cost and
    delay to enter that room that this Exit typeclass uses to allow
    or deny characters' passage. It also deducts movement points from
    their MV trait as they traverse.
    """

    def at_traverse(self, traversing_object, target_location):
        """
        Implements the actual traversal, using utils.delay to delay the move_to.
        """
        move_delay = self.destination.mv_delay
        move_cost = self.destination.mv_cost

        # make sure the character isn't already moving

        if traversing_object.nattributes.has('currently_moving'):
            traversing_object.msg("You are aleady moving. Use the 'stop' "
                                  "command and try again to change "
                                  "destinations.")
            return

        # check the movement cost

        if (hasattr(traversing_object, 'traits') and
                'MV' in traversing_object.traits.all):
            if traversing_object.traits.MV.actual < move_cost:
                traversing_object.msg('Moving so far so fast has worn you out. '
                                      'You pause for a moment to gather your '
                                      'composure.')
                return

        # then handle the move with the appropriate delay

        def move_callback():
            "This callback will be called by utils.delay after move_delay seconds."
            source_location = traversing_object.location
            if traversing_object.move_to(target_location):
                # deduct MV cost for the move
                if (hasattr(traversing_object, 'traits') and
                        'MV' in traversing_object.traits.all):
                    traversing_object.traits.MV.current -= move_cost

                # tell any maps to update
                for held_object in traversing_object.contents:
                    if isinstance(held_object, Map):
                        held_object.parent_did_move_from(source_location, self)

                self.at_after_traverse(traversing_object, source_location)
            else:
                if self.db.err_traverse:
                    # if exit has a better error message, let's use it.
                    self.caller.msg(self.db.err_traverse)
                else:
                    # No shorthand error message. Call hook.
                    self.at_failed_traverse(traversing_object)
            # clean up the 'currently_moving' ndb attribute
            if traversing_object.nattributes.has('currently_moving'):
                del traversing_object.ndb.currently_moving

        if move_delay > 0:
            start_msg = self.destination.db.msg_start_move or "You start moving {exit}."
            traversing_object.msg(start_msg.format(exit=self.key))
            # create a delayed movement
            deferred = utils.delay(move_delay, callback=move_callback)
            # we store the deferred on the character, this will allow us
            # to abort the movement. We must use an ndb here since
            # deferreds cannot be pickled.
            traversing_object.ndb.currently_moving = deferred
        else:
            # delay is 0, so we just run the callback now
            move_callback()
