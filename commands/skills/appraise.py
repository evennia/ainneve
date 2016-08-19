from commands.command import MuxCommand
from world.economy import value_to_coin
from world.rulebook import skill_check
from time import time

class CmdAppraise(MuxCommand):
    """
    appraise an item

    Usage:
      appraise <item>
      appr <item>

    Indicates the approximate value of an item in your inventory.
    The higher the Appraise skill, the better the approximation will be.
    """
    key = "appraise"
    aliases = ["appr"]
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
            caller.msg("You do not have %s." % args)
            return
        
        if not hasattr(obj, "value"):
            caller.msg("%s cannot be appraised." % obj.name.capitalize())

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

        #caller.msg("initial lose list: " + str(caller.ndb.appr_lose))
        #caller.msg("initial win list: " + str(caller.ndb.appr_win))

        lose = caller.ndb.appr_lose
        reroll_time = 3600 # how much time one has to wait before rerolling
                           # the appraise skill on the same type of item

        if lose.has_key(obj.name):
            if ct - lose[obj.name] <= reroll_time:
                #caller.msg("Using lose record from %f" % lose[obj.name])

                caller.msg("You have already attempted to appraise %s " %
                    obj.name +
                    "recently and must wait a while before trying again.")
                return
            else:
                # clear the record of the item
                #caller.msg("Clearing appraise check loss record from %f" %
                #    lose[obj.name])

                lose.pop(obj.name)        

        # check if the object has already been successfully appraised recently.
        # if not, run the appraise skill check.

        win = caller.ndb.appr_win

        if win.has_key(obj.name):
            if ct - win[obj.name] <= reroll_time:
                #caller.msg("Using win record from %f" % win[obj.name])

                self.display(obj)
                return
            else:
                    # clear the record of the item
                #caller.msg("Clearing appraise check win record from %f" %
                #    win[obj.name])

                caller.ndb.appr_win.pop(obj.name)

            # run the skill check again
        if skill_check(caller.skills.appraise.actual):
            #caller.msg("Appraise skill check successful")
            self.display(obj)

               #add a record of the item to the win list
            win[obj.name] = ct
        else:
            #caller.msg("Appraise skill check unsuccessful")

            caller.msg("You cannot tell the value of %s." % obj.name)

               #add a record of the item to the lose list
            lose[obj.name] = ct


        #caller.msg("final lose list: " + str(lose))
        #caller.msg("final win list: " + str(win))

        return

    def display(self, obj):
        # display the value of the item
        coin = value_to_coin(obj.db.value)

        if coin:
            cc = "%d CC" % coin['CC']
            if coin['GC'] == 0:
                gc = ""
                sc = " and "
            else:
                gc = " and %d GC" % coin['GC']
                sc = ", "
            if coin['SC'] == 0:
                sc = ""
            else:
                sc += "%d SC" % coin['SC']
            self.caller.msg("The value of %s is %s%s%s" % 
                (obj.name, cc, sc, gc))
        else:
            self.caller.msg("%s has no value." % obj.name.capitalize())


# test case: generate item, give supramaximal appraise skill to the character, 
# apply the appraise skill twice



