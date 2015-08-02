import plugger

from race import Race

def load_race(race):
    path = __name__ + '.' + race.lower() + '.' + race.title()
    race_class = plugger.load_plugin_class(path)
    return race_class()
