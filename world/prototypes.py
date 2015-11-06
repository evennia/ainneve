# -*- coding: UTF-8 -*-

# Generic starter gear

STARTER_SHIRT = {"key": "a linen tunic",
                 "desc": "Made of rough linen, this shirt's only " +
                         "value is its utility. Off-white and poorly " +
                         "fitting, it is otherwise unremarkable.",
                 "typeclass": "typeclasses.armors.SleevedShirt",
                 "locks": ";".join(("puppet:none()",
                                    "equip:perm(Players)")),
                 "weight": 1,
                 "value": 40,
                 "toughness": 0}

STARTER_PANTS = {"key": "linen pants",
                 "desc": "These homespun pants are light and comfortable, " +
                         "but provide little to no protection.",
                 "typeclass": "typeclasses.armors.Legwear",
                 "locks": ";".join(("puppet:none()",
                                    "equip:perm(Players)")),
                 "weight": 2,
                 "value": 50,
                 "toughness": 0}

STARTER_SHOES = {"key": "homespun shoes",
                 "desc": "The woven soles of these shoes are soft " +
                         "and provide little protection against " +
                         "rocky ground.",
                 "typeclass": "typeclasses.armors.Footwear",
                 "locks": ";".join(("puppet:none()",
                                    "equip:perm(Players)")),
                 "weight": 1,
                 "value": 30,
                 "toughness": 0}

