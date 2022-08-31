
from evennia import create_script
from evennia.contrib.grid import wilderness
from world.overworld.provider import OverworldMapProvider


OVERWORLD_NAME = "overworld"


def create_overworld():
    """
    Creates a new wilderness map. Does nothing if a wilderness map already
    exists with the same name.

    Args:
        name (str, optional): the name to use for that wilderness map
        mapprovider (WildernessMap instance, optional): an instance of a
            WildernessMap class (or subclass) that will be used to provide the
            layout of this wilderness map. If none is provided, the default
            infinite grid map will be used.

    """
    # TODO Should this be in the Script Class?
    if wilderness.WildernessScript.objects.filter(db_key=OVERWORLD_NAME).exists():
        # Don't create two wildernesses with the same name
        return

    script = create_script(Overworld, key=OVERWORLD_NAME, persistent=True, autostart=True)
    script.db.mapprovider = OverworldMapProvider()
    script.start()

    return script


def enter_overworld(obj, coordinates=(0, 0)):
    """
    Moves obj into the wilderness. The wilderness needs to exist first and the
    provided coordinates needs to be valid inside that wilderness.

    Args:
        obj (object): the object to move into the wilderness
        coordinates (tuple), optional): the coordinates to move obj to into
            the wilderness. If not provided, defaults (0, 0)
        name (str, optional): name of the wilderness map, if not using the
            default one

    Returns:
        bool: True if obj successfully moved into the wilderness.
    """
    script = Overworld.get_instance()
    if script.is_valid_coordinates(coordinates):
        script.move_obj(obj, coordinates)
        return True
    else:
        return False


class Overworld(wilderness.WildernessScript):
    _INSTANCE = None

    @classmethod
    def get_instance(cls):
        if Overworld._INSTANCE:
            return Overworld._INSTANCE

        if not Overworld.objects.filter(db_key=OVERWORLD_NAME).exists():
            script = create_overworld()
        else:
            script = Overworld.objects.get(db_key=OVERWORLD_NAME)

        script.at_start()

        Overworld._INSTANCE = script

        return script

    def at_script_creation(self):
        super().at_script_creation()
        # TODO Generate exits for landmarks
