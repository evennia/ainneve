"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

from evennia.utils import search, dedent

def at_initial_setup():
    limbo = search.objects('Limbo')[0]
    limbo.db.desc = dedent("""
        Welcome to |mAinneve|n, the example game for Evennia!

        The project is still in early development, and we welcome your contributions.

        |YDeveloper/Builder Resources|n
          * Issue tracking: https://github.com/evennia/ainneve/issues
          * Discussion list: https://groups.google.com/forum/?fromgroups#!categories/evennia/ainneve
          * Ainneve Wiki: https://github.com/evennia/ainneve/wiki
          * Evennia Developer IRC: http://webchat.freenode.net/?channels=evennia

        |YGetting Started|n
          As Account #1 you can use the |w@batchcmd|n or |w@batchcode|n commands to
          build components of Ainneve, or the entire world (once it has been created).

          Build scripts are in the |wworld/content/{area name}/|n directories and have |w*.ev|n or |w*.py|n extensions.

        """)

