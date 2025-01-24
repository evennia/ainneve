"""
Webclient based on websockets.

Subclasses the core Evennia websocket client - check the official docs for more information

"""
import json
import html
import re

from django.conf import settings
from evennia.utils import ansi, class_from_module

from .text2html import parse_html


_RE_SCREENREADER_REGEX = re.compile(
    r"%s" % settings.SCREENREADER_REGEX_STRIP, re.DOTALL + re.MULTILINE
)
_BASE_SESSION_CLASS = class_from_module(settings.BASE_SESSION_CLASS)

from evennia.server.portal.webclient import WebSocketClient as BaseWSClient


class WebSocketClient(BaseWSClient):
    """
    Implements the server-side of the Websocket connection.
    """

    def send_text(self, *args, **kwargs):
        """
        Send text data. This will pre-process the text for
        color-replacement, conversion to html etc.

        Args:
            text (str): Text to send.

        Keyword Args:
            options (dict): Options-dict with the following keys understood:
                - raw (bool): No parsing at all (leave ansi-to-html markers unparsed).
                - nocolor (bool): Clean out all color.
                - screenreader (bool): Use Screenreader mode.
                - send_prompt (bool): Send a prompt with parsed html

        """
        if args:
            args = list(args)
            text = args[0]
            if text is None:
                return
        else:
            return

        flags = self.protocol_flags

        options = kwargs.pop("options", {})
        raw = options.get("raw", flags.get("RAW", False))
        client_raw = options.get("client_raw", False)
        nocolor = options.get("nocolor", flags.get("NOCOLOR", False))
        screenreader = options.get("screenreader", flags.get("SCREENREADER", False))
        prompt = options.get("send_prompt", False)

        if screenreader:
            # screenreader mode cleans up output
            text = ansi.parse_ansi(text, strip_ansi=True, xterm256=False, mxp=False)
            text = _RE_SCREENREADER_REGEX.sub("", text)
        cmd = "prompt" if prompt else "text"
        if raw:
            if client_raw:
                args[0] = text
            else:
                args[0] = html.escape(text)  # escape html!
        else:
            args[0] = parse_html(text, strip_ansi=nocolor)

        # send to client on required form [cmdname, args, kwargs]
        self.sendLine(json.dumps([cmd, args, kwargs]))

    def send_chaninfo(self, channid, channame, subbed, *args, **kwargs):
        """
        Send channel information and subscription status to the client

        Args:
            channid (int)  -  the channel's ID number
            channame (str) -  the channel's name
            subbed (bool)  -  the subscription status
        """
        options = kwargs.pop("options", {})
        arglist = [channid, channame, subbed]

        # send to client on required form [cmdname, args, kwargs]
        self.sendLine(json.dumps(["chaninfo", arglist, kwargs]))

    def send_map(self, *args, **kwargs):
        """
        Parses the args for the `map` protocol command to convert style flags to
        HTML before sending through the wire.
        """
        args = [parse_html(arg) for arg in args]

        # send to client on required form [cmdname, args, kwargs]
        self.sendLine(json.dumps(["map", args, kwargs]))

    def data_in(self, **kwargs):
        if kwargs.get("ping"):
            # this is just a keepalive for the protocol...
            self.sendLine(json.dumps(["pong", "", ""]))
            return
        super().data_in(**kwargs)
