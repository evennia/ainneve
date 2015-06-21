class Trait(object):
    """
    This creates an easy to use trait for an object or character that has an
    automatically updating "current" field and can be made static.

    The Trait class can take the following arguments:
        name - the name of the trait. defaults to ""
        data - the data structure of the trait. defaults to:
            {'current': 0, 'base': 0, 'mod':0} but can have additional
            pieces of data added.
        static - whether or not the trait is static (current always equals max)
        overflow - allow it to go over its max if dynamic

    The Trait class has the following properties:
        actual/max - the maximum possible value of the trait
                     this adds the "base" value and any "mod" values added
        current - what is the trait currently at
                  if static, this will return actual/max
        fields - gives a list object of the trait's fields with types
        base - base amount of the Trait
        mod - modifier on the Trait, affects base
        current - semi-automatically updating base + mod

    The Trait class has the following methods:
        maximize - set 'current' value to max/actual
        fill - alias for maximize
        reset - clears any mods and then maximizes
        clear_mods - sets mod to 0

    Example usages:
        Dynamic trait:
            health = Trait("Health")
            health.base = 100
            health.current # returns 0
            health.fill()
            health.current # returns 100

        Overflow:
            health = Trait("health", base=25, mod=0)
            health.fill()
            health.current += 200 # try to add 200 when already max
            health.current # 25, overflow=False won't allow it
            health.overflow = True
            health.current += 200
            health.current # 225, overflow=True will allow it

        Static trait:
            dodge_chance = Trait("Dodge Chance", static=True)
            dodge_chance.base = 20 (no need to fill, because it is static)
            dodge_chance.current # returns 20

        Buff/Debuff a trait:
            This works for both static and dynamic traits.

            health = Trait("Health")
            health.base = 100
            health.fill()
            health.current # returns 100
            health.mod = -20
            health.current # returns 100 if dynamic
            health.maximize()
            health.current # returns 80

        Dealing with multiple modifiers:
            health = Trait("Health")
            health.base = 100
            health.mod = 100 # we get a +100 max health buff
            health.mod -= 30) # we get a -30 health debuff
            health.maximize()
            health.current # returns 170
            health.reset() # removes all mods and fills
            health.current # returns 100
    """
    def __init__(
        self,
        name="",
        base=0,
        mod=0,
        static=False,
        overflow=False,
        **kwargs
    ):
        self.name = name.title()
        self.static = static
        self.overflow = overflow
        self.data = {
            'base': base,
            'mod': mod,
            'current': 0
        }
        for key, value in kwargs.iteritems():
            self.data[key] = value

    def __str__(self):
        return "%s:\t\t%s" % (self.name, self.current)

    def __unicode__(self):
        return u"%s:\t\t%s" % (self.name, self.current)

    @property
    def actual(self):
        return self.data['base'] + self.data['mod']

    @property
    def base(self):
        return self.data['base']

    @base.setter
    def base(self, amount):
        if type(amount) in [int, float]:
            self.data['base'] = amount
        else:
            return False

    @property
    def current(self):
        if self.static:
            return self.actual
        else:
            return self.data['current']

    @current.setter
    def current(self, amount):
        if type(amount) in [int, float]:
            if (amount >= self.max) and not self.overflow:
                self.data['current'] = self.max
            else:
                self.data['current'] = amount
        else:
            return False

    @property
    def max(self):
        return self.actual

    @property
    def mod(self):
        return self.data['mod']

    @mod.setter
    def mod(self, amount):
        if type(amount) in [int, float]:
            self.data['mod'] = amount
            # if this is a dynamic trait, when a mod is applied
            # we should update current immediately
            if not self.static:
                self.maximize()
        else:
            return False

    def maximize(self):
        self.current = self.actual

    def fill(self):
        self.maximize()

    def reset(self):
        self.clear_mods()
        self.maximize()

    def clear_mods(self):
        self.mod = 0
