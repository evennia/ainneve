import inspect
from evennia.utils import evmenu
from evennia import Command
from evennia import CmdSet
from evennia import DefaultObject
from evennia.commands.default.building import ObjManipCommand
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.items import Item
from world.economy import format_coin as as_price
from world.economy import transfer_funds, InsufficientFunds, value_to_coin
from evennia.utils.create import create_object
from evennia.utils.utils import inherits_from

def get_wares(caller):
    """
    Gets items located in the designated storeroom of the caller's location with a price assigned
    Only descendants of the Item typeclass are eligible for sale
    """
    return [ware for ware in caller.location.db.storeroom.contents if inherits_from(ware, Item) and ware.db.value]

def menunode_shopfront(caller):
    "This is the top-menu screen."

    shopname = caller.location.key
    caller.ndb._menutree.npc_shop_wares = get_wares(caller)

    text = "*** Welcome to %s! ***\n" % shopname
    if caller.ndb._menutree.npc_shop_wares:
        text += "   Things for sale (choose 1-%i to inspect);" \
                " quit to exit:" % len(caller.ndb._menutree.npc_shop_wares)
    else:
        text += "   There is nothing for sale; quit to exit."

    options = []
    for ware in caller.ndb._menutree.npc_shop_wares:
        # add an option for every ware in store
        options.append({"desc": "%s (%s)" %
                                (ware.key, as_price(ware.db.value)),
                        "goto": "menunode_inspect_and_buy"})
    return text, options


def menunode_inspect_and_buy(caller, raw_input):
    """
    Sets up the buy menu screen,
    or informs the player that the ware is no longer available
    """

    iware = int(raw_input) - 1
    ware = caller.ndb._menutree.npc_shop_wares[iware]

    def purchase_item(caller):
            """Process item purchase."""
            try:
                # this will raise exception if
                # caller doesn't have enough funds
                if ware.location == caller.location.db.storeroom and ware.db.value:
                    transfer_funds(caller, None, ware.db.value)
                    ware.move_to(caller, quiet=True)
                    ware.at_get(caller)
                    rtext = "You pay {} and purchase {}".format(
                                as_price(ware.db.value),
                                ware.key
                             )
                else:
                    rtext = "{} is no longer available.".format(
                            ware.key.capitalize())
            except InsufficientFunds:
                rtext = "You do not have enough money to buy {}.".format(
                            ware.key)
            caller.msg(rtext)

    if ware.location == caller.location.db.storeroom and ware.db.value:
        # If the item's still in stock and has not been removed from sale
        text = "You inspect %s:\n\n%s" % (ware.key, ware.db.desc)
        options = ({"desc": "Buy %s for %s" % \
                        (ware.key, as_price(ware.db.value) or 1),
                "goto": "menunode_shopfront",
                "exec": purchase_item},
               {"desc": "Look for something else",
                "goto": "menunode_shopfront"})
    else:
        text = "{} is no longer available".format(ware.key.capitalize())
        options = ({"desc": "Look for something else",
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
class CmdBuildShop(ObjManipCommand):
    """
    Build a new shop

    Usage:
        @buildshop shopname[;alias;alias...], shopname...

    This will create new NPCshop rooms as well as linked store rooms
    (named simply <storename>-storage) for the wares on sale and exits
    linking the builder's current room to the shops. The store room will
    be accessed through a locked door in the shop.

    You can build many shops by comma-separating their names, and assign
    aliases with semicolons as you would with @create.
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
        super(CmdBuildShop, self).parse()
        for objdef in self.lhs_objs:
            shopname = objdef['name']
            aliases = objdef['aliases']
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
                                               aliases=["storage", "store room", "storeroom"],
                                               location=shop,
                                               destination=storeroom,
                                               home=shop)
            storeroom_exit = create_object(Exit,
                                           key="shop",
                                           aliases=["exit", "back", "out", "door", "o"],
                                           location=storeroom,
                                           destination=shop,
                                           home=storeroom)
            shop_entrance = create_object(Exit,
                                          key=shopname,
                                          location=self.caller.location,
                                          destination=shop,
                                          aliases=aliases,
                                          home=self.caller.location)
            shop_exit = create_object(Exit,
                                      key="front door",
                                      aliases=["front", "exit", "out", "o"],
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
        try:
            item_name, value = self.args.split()
        except:
            self.caller.msg("I'm afraid I don't understand. Please check your syntax.")
            return
        item = self.caller.search(item_name,
                                  location=self.caller.location,
                                  typeclass='typeclasses.items.Item',
                                  quiet=True)
        if not item:
            self.caller.msg("I can't find a sellable Item called '{}' here.".format(
                item_name
            ))
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
    "Commands available from within a shop storeroom"
    def at_cmdset_creation(self):
        self.add(CmdPrice())

class StoreRoom(Room):
    "Every shop has a designated storeroom which holds the inventory and provides commands for inventory management"

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