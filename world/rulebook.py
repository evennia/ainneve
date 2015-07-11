from random import randint


def roll_stat():
    rolls = []
    stat = 0

    # roll a 4d6
    for stat in range(0, 4):
        rolls.append(randint(1, 6))
    # order from high to low
    rolls = sorted(rolls, reverse=True)
    # drop lowest roll
    rolls.pop()

    for roll in rolls:
        stat += roll

    return stat


def roll_stats(amount):
    stats = []

    for stat in range(0, amount):
        stats.append(roll_stat())

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
