"""
Customized version of the core text2html for use with the custom client.

The default text2html has a very specific hardcoded function call for MXP links
which is not compatible with this client, so it is replaced here.
"""
from evennia.utils.text2html import TextToHTMLparser


class ModdedHTMLParser(TextToHTMLparser):
    def sub_mxp_links(self, match):
        """
        Helper method to be passed to re.sub, replaces MXP links with HTML code.

        Args:
            match (re.Matchobject): Match for substitution.

        Returns:
            text (str): Processed text.

        """
        cmd, text = [grp.replace('"', "\\&quot;") for grp in match.groups()]
        val = rf'<span class="mxplink" data-command="{cmd}">{text}</span>'
        return val


MODDED_PARSER = ModdedHTMLParser()


def parse_html(text, strip_ansi=False):
    return MODDED_PARSER.parse(text, strip_ansi=strip_ansi)
