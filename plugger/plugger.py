import sys
from importlib import import_module
from inspect import trace


def make_iter(obj):
    "Makes sure that the object is always iterable."
    return not hasattr(obj, '__iter__') and [obj] or obj


def load_plugin(path):
    try:
        plugin = import_module(path)
    except ImportError:
        if len(trace()) > 2:
            exc = sys.exc_info()
            raise exc[1], None, exc[2]
    return plugin
# alias
load_module = load_plugin


def load_plugin_class(path, defaultpaths=None):
    cls = None
    if defaultpaths:
        paths = [path] + [
            "%s.%s" % (dpath, path) for dpath in make_iter(defaultpaths)
        ] if defaultpaths else []
    else:
        paths = [path]

    for testpath in paths:
        if "." in path:
            testpath, clsname = testpath.rsplit('.', 1)
        else:
            raise ImportError("The path '%s' is not in the form\
 of modulepath.Classname" % path)
        try:
            mod = import_module(testpath)
        except ImportError:
            if len(trace()) > 2:
                exc = sys.exc_info()
                raise exc[1], None, exc[2]
            else:
                continue

        try:
            cls = getattr(mod, clsname)
        except AttributeError:
            if len(trace()) > 2:
                exc = sys.exc_info()
                raise exc[1], None, exc[2]

    if not cls:
        err = "Could not load plugin class '%s'" % path
        if defaultpaths:
            err += "\nPaths searched:\n\t%s" % "\n\t".join(paths)
        else:
            err += "."
        raise ImportError(err)
    return cls
