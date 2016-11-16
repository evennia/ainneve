from evennia.utils import evmenu
from evennia import Command
from evennia import CmdSet
from evennia import DefaultObject
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from evennia.utils.create import create_object


def menunode_shopfront(caller):
    "This is the top-menu screen."

    shopname = caller.location.key
    wares = caller.location.db.storeroom.contents

    # Wares includes all items inside the storeroom, including the
    # door! Let's remove that from our for sale list.
    wares = [ware for ware in wares if ware.key.lower() != "door"]

    text = "*** Welcome to %s! ***\n" % shopname
    if wares:
        text += "   Things for sale (choose 1-%i to inspect);" \
                " quit to exit:" % len(wares)
    else:
        text += "   There is nothing for sale; quit to exit."

    options = []
    for ware in wares:
        # add an option for every ware in store
        options.append({"desc": "%s (%s gold)" %
                                (ware.key, ware.db.gold_value or 1),
                        "goto": "menunode_inspect_and_buy"})
    return text, options


def menunode_inspect_and_buy(caller, raw_input):
    "Sets up the buy menu screen."

    wares = caller.location.db.storeroom.contents
    iware = int(raw_input) - 1
    ware = wares[iware]
    value = ware.db.gold_value or 1
    wealth = caller.db.gold or 0
    text = "You inspect %s:\n\n%s" % (ware.key, ware.db.desc)

    def buy_ware_result(caller):
        "This will be executed first when choosing to buy."
        if wealth >= value:
            rtext = "You pay %i gold and purchase %s!" % \
                    (value, ware.key)
            caller.db.gold -= value
            ware.move_to(caller, quiet=True)
        else:
            rtext = "You cannot afford %i gold for %s!" % \
                    (value, ware.key)
        caller.msg(rtext)

    options = ({"desc": "Buy %s for %s gold" % \
                        (ware.key, ware.db.gold_value or 1),
                "goto": "menunode_shopfront",
                "exec": buy_ware_result},
               {"desc": "Look for something else",
                "goto": "menunode_shopfront"})

    return text, options


class CmdBuy(Command):
    """
    Start to do some shopping

    Usage:
      buy
      shop
      browse

    This will allow you to browse the wares of the
    current shop and buy items you want.
    """
    key = "buy"
    aliases = ("shop", "browse")

    def func(self):
        "Starts the shop EvMenu instance"
        evmenu.EvMenu(self.caller,
                      "typeclasses.npcshop",
                      startnode="menunode_shopfront")


class ShopCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdBuy())


# class for our front shop room
class NPCShop(Room):
    def at_object_creation(self):
        super(NPCShop, self).at_object_creation()
        # we could also use add(ShopCmdSet, permanent=True)
        self.cmdset.add_default(ShopCmdSet)
        self.db.storeroom = None


# command to build a complete shop (the Command base class
# should already have been imported earlier in this file)
class CmdBuildShop(Command):
    """
    Build a new shop

    Usage:
        @buildshop shopname

    This will create a new NPCshop room
    as well as a linked store room (named
    simply <storename>-storage) for the
    wares on sale. The store room will be
    accessed through a locked door in
    the shop.
    """
    key = "@buildshop"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        "Create the shop rooms"
        if not self.args:
            self.msg("Usage: @buildshop <storename>")
            return
        # create the shop and storeroom
        shopname = self.args.strip()
        shop = create_object(NPCShop,
                             key=shopname,
                             location=None,
                             nohome=True)
        shop.at_object_creation()

        storeroom = create_object(Room,
                                  key="%s-storage" % shopname,
                                  location=None,
                                  nohome=True)
        storeroom.at_object_creation()
        shop.db.storeroom = storeroom
        # create a door between the two
        storeroom_entrance = create_object(Exit,
                                  key="back door",
                                  aliases=["storage", "store room"],
                                  location=shop,
                                  destination=storeroom,
                                  home=shop)
        storeroom_exit = create_object(Exit,
                                       key="door",
                                       location=storeroom,
                                       destination=shop,
                                       home=storeroom)
        shop_exit = create_object(Exit,
                                  key="front door",
                                  location=shop,
                                  destination=None,
                                  home=shop)
        # make a key for accessing the store room
        storeroom_key_name = "%s-storekey" % shopname
        storeroom_key = create_object(DefaultObject,
                                      key=storeroom_key_name,
                                      location=self.caller,
                                      home=self.caller)
        # only allow chars with this key to enter the store room
        storeroom_entrance.locks.add("traverse:holds(%s)" % storeroom_key_name)

        # inform the builder about progress
        self.caller.msg("The shop %s was created!" % shop)
