from evennia import default_cmds
from world.economy import format_coin
from world.rulebook import skill_check
from time import time

class CmdAppraise(default_cmds.MuxCommand):
    """
    appraise an item

    Usage:
      appraise <item>
      app <item>

    Determines the properties of an item in your inventory.
    The higher the Appraise skill, the greater the chance that the use of
    the appraise action will be successful.
    """
    key = "appraise"
    aliases = ["app"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if not args:
            caller.msg("Appraise what?")
            return

        # get the argument of the command        
        obj = caller.search(args)
        
        if not obj:
            caller.msg("You do not have {0}.".format(args))
            return
        
        if not obj.attributes.has("value"):
            caller.msg("{0} cannot be appraised.".format(obj.name.capitalize()))

        ct = time() # current time; we need this to check if the last appraise
                    # on the item is recent

            # if they don't exist, create the appraise roll win and lose lists,
            # which list all items that appraise was attempted on and their
            # timestamps

        if not hasattr(caller.ndb, "appr_lose") or not caller.ndb.appr_lose:
            caller.ndb.appr_lose = {}
        
        if not hasattr(caller.ndb, "appr_win") or not caller.ndb.appr_win:
            caller.ndb.appr_win = {}

        # check if the object has failed to be appraised recently. If so,
        # prohibit further appraisal.

        lose = caller.ndb.appr_lose
        reroll_time = 3600 # how much time one has to wait before rerolling
                           # the appraise skill on the same type of item

        if(obj.dbref in lose):
            if ct - lose[obj.dbref] <= reroll_time:
                caller.msg("You have already attempted to appraise " + 
                    obj.name +
                    " recently and must wait a while before trying again.")
                return
            else:
                # clear the record of the item
                lose.pop(obj.dbref)        

        # check if the object has already been successfully appraised recently.
        # if not, run the appraise skill check.

        win = caller.ndb.appr_win

        if(obj.dbref in win):
            if ct - win[obj.dbref] <= reroll_time:
                self.display(obj)
                return
            else:
                    # clear the record of the item
                caller.ndb.appr_win.pop(obj.dbref)

            # run the skill check again
        if skill_check(caller.skills.appraise.actual):
            self.display(obj)

               #add a record of the item to the win list
            win[obj.dbref] = ct
        else:
            caller.msg(
        "You cannot tell the qualities of {0}.".format(obj.name))

               #add a record of the item to the lose list
            lose[obj.dbref] = ct
        return

    def display(self, item):
        # display the value of the item
        data = ""
        if item.attributes.has('value'):            
            data += "Value: {0}\n".format(format_coin(item.db.value))
        if item.attributes.has('weight'):
            data += "Weight: {0}\n".format(item.db.weight)
        if item.attributes.has('damage'):
            data += "|rDamage: {:>2d}|n \n".format(item.db.damage)
        if item.attributes.has('range'):
            data += "|GRange: {:>2d}|n \n".format(item.db.range)
        if item.attributes.has('toughness'):
            data += "|yToughness: {:>2d}|n".format(item.db.toughness)
        self.caller.msg(data)

    




# test case: generate item, give supramaximal appraise skill to the character, 
# apply the appraise skill twice



