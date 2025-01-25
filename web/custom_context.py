"""
This file adds on some global variables for all of the django websites, specifically
for the purpose of CACHE BUSTING.

Cache busting is a technique to prevent your end-users from having old, outdated
CSS and Javascript files cached in their browsers that might not work any more, without
forcing them to download the files every single time and waste everyone's bandwidth.

The function below is added to the settings file to make sure the globals are available.

(If you love this idea, you can modify your base website template too with a cache-buster
timestamp for your base website CSS file and add it here!)

"""
from os.path import getmtime
from random import choice

WEBCLIENT_CSS_VERSION = round(getmtime("web/static/webclient/css/webclient.css"))
WEBCLIENT_JS_VERSION = round(getmtime("web/static/webclient/js/webclient.js"))


def extra_context(request):
    """
    Returns common Evennia-related context stuff, which is automatically added
    to context of all views.

    """
    return {
        "client_css_version": WEBCLIENT_CSS_VERSION,
        "client_js_version": WEBCLIENT_JS_VERSION,
    }
