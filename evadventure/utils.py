_OBJ_STATS = """
|c{key}|n
Value: ~|y{value}|n coins{carried}

{desc}

Slots: |w{size}|n, Used from: |w{use_slot_name}|n
Quality: |w{quality}|n, Uses: |w{uses}|n
Attacks using |w{attack_type_name}|n against |w{defense_type_name}|n
Damage roll: |w{damage_roll}|n
""".strip()


def get_obj_stats(obj, owner=None):
    """
    Get a string of stats about the object.

    Args:
        obj (Object): The object to get stats for.
        owner (Object): The one currently owning/carrying `obj`, if any. Can be
            used to show e.g. where they are wielding it.
    Returns:
        str: A nice info string to display about the object.

    """
    return _OBJ_STATS.format(
        key=obj.key,
        value=10,
        carried="[Not carried]",
        desc=obj.db.desc,
        size=1,
        quality=3,
        uses="infinite",
        use_slot_name = "backpack",
        attack_type_name = "strength",
        defense_type_name = "armor",
        damage_roll = "1d6",
    )
