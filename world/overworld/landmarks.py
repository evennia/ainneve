"""
Landmarks represents an Exit to the proper area instance (Static Or Dynamic).
They will also be available as destinations for the 'travel' command.
To add new ones you only need to add a Landmark instance in the OverworldLandmarks class.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Landmark:
    name: str
    coordinates: tuple[int, int]
    room_prototype: str
    area_exit_prototype: str


class OverworldLandmarks:
    """ Simple class acting as repository for the landmarks """

    _cached_dict = None

    Whiterock_Kingdom = Landmark(
        name="Whiterock Kingdom",
        coordinates=(11, 23),
        room_prototype="wilderness_landmark_whiterock_kingdom",
        area_exit_prototype="wilderness_exit_to_whiterock_kingdom"
    )

    Tobichi_Forest = Landmark(
        name="Tobichi Forest",
        coordinates=(44, 18),
        room_prototype="wilderness_landmark_tobichi_forest",
        area_exit_prototype="wilderness_exit_to_tobichi_forest"
    )

    Furrato_Valley = Landmark(
        name="Furrato Valley",
        coordinates=(21, 20),
        room_prototype="wilderness_landmark_furrato_valley",
        area_exit_prototype="wilderness_exit_to_furrato_valley",
    )

    Riverport_Settlement = Landmark(
        name="Riverport Settlement",
        coordinates=(41, 31),
        room_prototype="wilderness_landmark_riverport_settlement",
        area_exit_prototype="wilderness_exit_to_riverport_settlement",
    )

    Selonna_Bay = Landmark(
        name="Selonna Bay",
        coordinates=(64, 28),
        room_prototype="wilderness_landmark_selonna_bay",
        area_exit_prototype="wilderness_exit_to_selonna_bay",
    )

    Renegade_Hideout = Landmark(
        name="Renegade's Hideout",
        coordinates=(7, 22),
        room_prototype="wilderness_landmark_renegade_hideout",
        area_exit_prototype="wilderness_exit_to_renegade_hideout",
    )

    Smuggler_Cove = Landmark(
        name="Smuggler's Cove",
        coordinates=(42, 3),
        room_prototype="wilderness_landmark_smuggler_cove",
        area_exit_prototype="wilderness_exit_to_smuggler_cove",
    )

    Taurosu_Tribe = Landmark(
        name="Taurosu Tribe",
        coordinates=(55, 45),
        room_prototype="wilderness_landmark_taurosu_tribe",
        area_exit_prototype="wilderness_exit_to_taurosu_tribe",
    )

    Tomu_Lake = Landmark(
        name="Tomu Lake",
        coordinates=(21, 14),
        room_prototype="wilderness_landmark_tomu_lake",
        area_exit_prototype="wilderness_exit_to_tomu_lake",
    )

    Goldgrass_Plains = Landmark(
        name="Goldgrass Plains",
        coordinates=(56, 48),
        room_prototype="wilderness_landmark_goldgrass_plains",
        area_exit_prototype="wilderness_exit_to_goldgrass_plains",
    )

    Soran_Castle = Landmark(
        name="Soran Castle",
        coordinates=(32, 4),
        room_prototype="wilderness_landmark_soran_castle",
        area_exit_prototype="wilderness_exit_to_soran_castle",
    )

    Cactus_Canyon = Landmark(
        name="Cactus Canyon",
        coordinates=(18, 42),
        room_prototype="wilderness_landmark_cactus_canyon",
        area_exit_prototype="wilderness_exit_to_cactus_canyon",
    )

    Litchbane_Keep = Landmark(
        name="Litchbane Keep",
        coordinates=(11, 54),
        room_prototype="wilderness_landmark_litchbane_keep",
        area_exit_prototype="wilderness_exit_to_litchbane_keep",
    )

    Yaban_Hinterlands = Landmark(
        name="Yaban Hinterlands",
        coordinates=(18, 42),
        room_prototype="wilderness_landmark_yaban_hinterlands",
        area_exit_prototype="wilderness_exit_to_yaban_hinterlands",
    )

    Sun_Temple = Landmark(
        name="Sun Temple",
        coordinates=(38, 6),
        room_prototype="wilderness_landmark_sun_temple",
        area_exit_prototype="wilderness_exit_to_sun_temple",
    )

    Moon_Temple = Landmark(
        name="Moon Temple",
        coordinates=(51, 45),
        room_prototype="wilderness_landmark_moon_temple",
        area_exit_prototype="wilderness_exit_to_moon_temple",
    )

    Earth_Temple = Landmark(
        name="Earth Temple",
        coordinates=(12, 56),
        room_prototype="wilderness_landmark_earth_temple",
        area_exit_prototype="wilderness_exit_to_earth_temple",
    )

    Star_Temple = Landmark(
        name="Star Temple",
        coordinates=(68, 14),
        room_prototype="wilderness_landmark_star_temple",
        area_exit_prototype="wilderness_exit_to_star_temple",
    )

    Aether_Temple = Landmark(
        name="Aether Temple",
        coordinates=(12, 56),
        room_prototype="wilderness_landmark_aether_temple",
        area_exit_prototype="wilderness_exit_to_aether_temple",
    )

    Zeita_Palace = Landmark(
        name="Zeita Palace",
        coordinates=(11, 63),
        room_prototype="wilderness_landmark_zeita_palace",
        area_exit_prototype="wilderness_exit_to_zeita_palace",
    )

    Sarab_Oasis = Landmark(
        name="Sarab Oasis",
        coordinates=(21, 41),
        room_prototype="wilderness_landmark_sarab_oasis",
        area_exit_prototype="wilderness_exit_to_sarab_oasis",
    )

    Aiiro_Lake = Landmark(
        name="Aiiro Lake",
        coordinates=(42, 35),
        room_prototype="wilderness_landmark_aiiro_lake",
        area_exit_prototype="wilderness_exit_to_aiiro_lake",
    )

    Centaurian_Herdclan = Landmark(
        name="Centaurian 'Brownhoof' Herdclan",
        coordinates=(56, 24),
        room_prototype="wilderness_landmark_centaurian_herdclan",
        area_exit_prototype="wilderness_exit_to_centaurian_herdclan",
    )

    Acidmire_Marsh = Landmark(
        name="Acidmire Marsh",
        coordinates=(44, 10),
        room_prototype="wilderness_landmark_acidmire_marsh",
        area_exit_prototype="wilderness_exit_to_acidmire_marsh",
    )

    Aetherfen_Swamp = Landmark(
        name="Aetherfen Swamp",
        coordinates=(15, 55),
        room_prototype="wilderness_landmark_aetherfen_swamp",
        area_exit_prototype="wilderness_exit_to_aetherfen_swamp",
    )

    Highborn_Settlement = Landmark(
        name="Highborn Settlement",
        coordinates=(27, 11),
        room_prototype="wilderness_landmark_highborn_settlement",
        area_exit_prototype="wilderness_exit_to_highborn_settlement",
    )

    @classmethod
    def _get_cached_dict(cls):
        if not cls._cached_dict:
            new_dict = {key: value for key, value in cls.__dict__.items() if isinstance(value, Landmark)}
            cls._cached_dict = new_dict

        return cls._cached_dict

    @classmethod
    def items(cls):
        return cls._get_cached_dict().items()

    @classmethod
    def values(cls):
        return cls._get_cached_dict().values()
