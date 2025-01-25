"""
This file implements two custom inputfuncs that the webclient uses to dynamically
load information. Modify or reference them and how they're called by the client to
create your own as needed.

(See the original documentation string for this file for more information on inputfuncs)
"""


def get_map(session, *args, **kwargs):
    """Custom inputfunc to request the character's visible map."""
    mapstr = None
    if (obj := session.puppet) and obj.location:
        # this is where you fetch the map string for the character and their location
        # e.g. mapstr = obj.location.get_map(obj)
        pass

    if not mapstr:
        # no valid map so just don't do anything
        return

    # send the message
    session.msg(map=mapstr)


def get_channels(session, *args, **kwargs):
    """Request channel information for all channels the sender's account is subscribed to"""
    if session.account:
        from typeclasses.channels import Channel

        # this will send custom protocol-command messages to the session for each channel they're connected to
        for chan in Channel.objects.all():
            if chan.has_connection(session.account):
                session.msg(chaninfo=(chan.id, chan.key, True))
