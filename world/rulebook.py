from random import randint


def roll_stat():
    """rolls the 4d6, drop lowest and sums the remaining dice."""

    # roll a 4d6
    rolls = [randint(1, 6) for _ in range(4)]
    # order from high to low
    rolls = sorted(rolls, reverse=True)
    # drop lowest roll
    rolls.pop()

    stat = sum(rolls)

    return stat


def roll_stats(amount):
    """rolls ``amount`` number of stats and returns list of result."""
    stats = [roll_stat() for _ in range(amount)]
    return sorted(stats, reverse=True)


def roll_percent(success):
    d1 = randint(0, 9)
    d2 = randint(0, 9)
    p = None

    d1 *= 10

    if d2 == 0:
        p = d1 + 10
    else:
        p = d1 + d2

    if p <= success:
        return True
    else:
        return False
