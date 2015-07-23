class Ability(object):
    """
    Basic ability object that can be used by both skills and spells
    """
    def __init__(self,name=""):
        self.name = name                    # Name of the ability
        self.description = "define me"      # How the abilities appears in the 'abilities' command
        self.type = ""                      # Ability type [skill/spell]
        self.level = 0                      # Current level of the ability
        self.max_level = 99                 # Maximum level the ability can be increased to

        self.use_delay = 0                  # How long does it take to execute on use
        self.modifier = 0                   # The modifier for this skill, i.e. damage value
        self.affects = {}                   # What affect is applied

        self.msg_to_caller = ""             # Text to show to the caller on use
        self.msg_to_target = ""             # Text to show to the target on use
        self.msg_to_room = ""               # Text to show to the room on use

        self.mana_cost = 0                  # How much mana does it take to use
        self.move_cost = 0                  # How much move does it take to use
        self.hp_cost = 0                    # How much hp does it take to cast

    def __str__(self):
        return "%s" % self.name
