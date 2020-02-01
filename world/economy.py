"""
Economy module.
"""
from evennia.utils.dbserialize import _SaverDict

# Constants

#: (int) copper coins
CC = 1

#: (int) silver coins
SC = 100

#: (int) gold coins
GC = 10000


_WALLET_KEYS = ('GC', 'SC', 'CC')


class InsufficientFunds(ValueError):
    """Represents an error in a financial transaction."""
    pass


def value_to_coin(value):
    """Given a base value in CC, return smallest number of coins."""
    if value:
        if isinstance(value, int):
            gc = value / GC
            value %= GC
            sc = value / SC
            cc = value % SC
            return dict(CC=cc, SC=sc, GC=gc)
        elif isinstance(value, (dict, _SaverDict)):
            return {c: v for c, v in value.items() if c in _WALLET_KEYS}
    return None

def coin_to_value(coins):
    """Given a dict of coin: value pairs, return the total value in CC.

    Args:
        coins (int, dict): dict of coin names and values; assumes CC if an int
    """
    if coins is None:
        return None
    if not isinstance(coins, (int, dict, _SaverDict)):
        raise TypeError("'coins' must be a dict of 'coin': count pairs.")
    if isinstance(coins, int):
        coins = {'CC': coins}
    return (coins.get('GC', 0) * GC +
            coins.get('SC', 0) * SC +
            coins.get('CC', 0))


def transfer_funds(src, dst, value_or_coin):
    """Transfers a given value from src wallet to dst wallet.

    Note:
        If either 'src' or 'dst' are None, the money is created
        or destroyed by this function.
    """
    src_val = coin_to_value(src.db.wallet) if src else 0
    dst_val = coin_to_value(dst.db.wallet) if dst else 0
    xfr_val = coin_to_value(value_or_coin)
    # check there's enough
    if src is not None and src_val < xfr_val:
        raise InsufficientFunds("Insufficient funds.")

    if src is not None:
        src.db.wallet = value_to_coin(src_val - xfr_val)

    if dst is not None:
        dst.db.wallet = value_to_coin((dst_val or 0) + xfr_val)


def format_coin(value_or_coin):
    """Returns a string representing a value as numbers of coins."""

    coins = value_to_coin(value_or_coin) or {'GC': 0, 'SC': 0, 'CC': 0}
    gc, sc, cc = coins.get('GC', 0), coins.get('SC', 0), coins.get('CC', 0)
    output = ""
    if gc:
        output += "|w{}|n GC ".format(gc)
    if sc:
        output += "|w{}|n SC ".format(sc)
    if cc:
        output += "|w{}|n CC".format(cc)
    if output == "":
        output = "0 CC"
    return output.strip()

