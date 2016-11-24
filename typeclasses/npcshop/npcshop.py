import inspect
from evennia.utils import evmenu
from evennia import Command
from evennia import CmdSet
from evennia import DefaultObject
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.items import Item
from world.economy import format_coin as as_price
from world.economy import transfer_funds, InsufficientFunds, value_to_coin
from evennia.utils.create import create_object

def get_wares(caller):
    wares = caller.location.db.storeroom.contents
    # Only descendants of the Item typeclass are eligible for sale
    return [ware for ware in wares if Item in inspect.getmro(ware.__class__) and ware.db.value]

def menunode_shopfront(caller):
    "This is the top-menu screen."

    shopname = caller.location.key
    wares = get_wares(caller)

    text = "*** Welcome to %s! ***\n" % shopname
    if wares:
        text += "   Things for sale (choose 1-%i to inspect);" \
                " quit to exit:" % len(wares)
    else:
        text += "   There is nothing for sale; quit to exit."

    options = []
    for ware in wares:
        # add an option for every ware in store
        options.append({"desc": "%s (%s)" %
                                (ware.key, as_price(ware.db.value) or 1),
                        "goto": "menunode_inspect_and_buy"})
    return text, options


def menunode_inspect_and_buy(caller, raw_input):
    "Sets up the buy menu screen."

    wares = get_wares(caller)
    iware = int(raw_input) - 1
    ware = wares[iware]
    text = "You inspect %s:\n\n%s" % (ware.key, ware.db.desc)

    def purchase_item(caller):
            """Process item purchase."""
            try:
                # this will raise exception if caller doesn't
                # have enough funds in their `db.wallet`
                transfer_funds(caller, None, ware.db.value)
                ware.move_to(caller, quiet=True)
                ware.at_get(caller)
                rtext = "You pay {} and purchase {}".format(
                            as_price(ware.db.value),
                            ware.key
                         )
            except InsufficientFunds:
                rtext = "You do not have enough money to buy {}.".format(
                            ware.key)
            caller.msg(rtext)

    options = ({"desc": "Buy %s for %s" % \
                        (ware.key, as_price(ware.db.value) or 1),
                "goto": "menunode_shopfront",
                "exec": purchase_item},
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
        print type(self.caller)
        print type(self.caller.db.wallet)
        evmenu.EvMenu(self.caller,
                      "typeclasses.npcshop.npcshop",
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

    This will create a new NPCshop room as well as a linked store room (named simply <storename>-storage) for the
    wares on sale and exits linking the builder's current room to the shop.
    The store room will be accessed through a locked door in the shop.
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

        storeroom = create_object(StoreRoom,
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
        shop_entrance = create_object(Exit,
                                      key=shopname,
                                      location=self.caller.location,
                                      destination=shop,
                                      home=self.caller.location)
        shop_exit = create_object(Exit,
                                  key="front door",
                                  location=shop,
                                  destination=self.caller.location,
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

class CmdPrice(Command):
    """
    Set the price of an item

    Usage:
        price item value

    This will set the price of an item while inside a storeroom.
    Value is counted in CC.
    """
    key = "price"
    help_category = "StoreRoom"

    def func(self):
        print self.args.split()
        try:
            item, value = self.args.split()
        except:
            self.caller.msg("I'm afraid I don't understand. Please check your syntax.")
            return
        item = self.caller.search(item,
                             location=self.caller.location,
                             typeclass='typeclasses.items.Item')
        if not item:
            self.caller.msg("I can't find that here.")
            return
        elif Item not in inspect.getmro(item.__class__):
            self.caller.msg("That's not valid for sale. Only wares deriving from the Item typeclass may be sold.")
            return
        else:
            try:
                value = int(value)
            except:
                self.caller.msg("Your price can only be an integer.")
                return
            item.db.value = value
            self.caller.msg("You set the price of {} to {}.".format(
                item,
                as_price(value)
            ))

class StoreRoomCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdPrice())

class StoreRoom(Room):

    def at_object_creation(self):
        super(StoreRoom, self).at_object_creation()
        self.cmdset.add_default(StoreRoomCmdSet)

    def return_appearance(self, caller):
        wares = []
        for item in self.contents:
            if item.db.value:
                wares.append(item.key)
        desc = super(StoreRoom, self).return_appearance(caller)
        for line in desc.split("\n"):
            if line.strip().split("(")[0] in wares:
                line = "|y" + line
            caller.msg(line)
        # caller.msg(desc)