
from evennia import create_script
from evennia.contrib.grid import wilderness
from evennia.utils import logger
from world.overworld.provider import OverworldMapProvider


class Overworld(wilderness.WildernessScript):
    _INSTANCE = None
    _NAME = "overworld"

    @classmethod
    def get_instance(cls):
        if cls._INSTANCE:
            return cls._INSTANCE

        if not Overworld.objects.filter(db_key=cls._NAME).exists():
            script = cls.create()
        else:
            script = Overworld.objects.get(db_key=cls._NAME)

        if not script.is_active:
            script.start()

        cls._INSTANCE = script

        return script

    @classmethod
    def enter(cls, obj, coordinates=(0, 0)):
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
        script = cls.get_instance()
        if script.is_valid_coordinates(coordinates):
            script.move_obj(obj, coordinates)
            return True
        else:
            return False

    @classmethod
    def create(cls):
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
        if Overworld.objects.filter(db_key=cls._NAME).exists():
            # Don't create two wildernesses with the same name
            return

        logger.info("Creating new instance of Overworld script...")
        script = create_script(Overworld, key=cls._NAME, persistent=True, autostart=True)
        script.db.mapprovider = OverworldMapProvider()
        script.start()

        return script
