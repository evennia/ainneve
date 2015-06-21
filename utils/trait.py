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

    The Trait class has the following properties:
        actual/max - the maximum possible value of the trait
                     this adds the "base" value and any "mod" values added
        current - what is the trait currently at
                  if static, this will return actual/max
        fields - gives a list object of the trait's fields

    The Trait class has the following methods:
        maximize - set 'current' value to max/actual
        fill - alias for maximize
        recover - alias for maximize
        get_base - get the base value of the trait
        set_base - update the base value of the trait
        get_mod - get the modifying value of the trait
        set_mod - set the modifying value of the trait
        get_field(field) - get the value of a custom field
        set_field(field, value) - set the value of a custom field
        delete_field(field) - delete a field from the trait. cannot delete the
            default fields (base, current, mod)
        add_field(field, value) - add a new field to the trait

    Example usages:
        Dynamic trait:
            health = Trait("Health")
            health.set_base(100)
            health.current # returns 0
            health.fill()
            health.current # returns 100

        Static trait:
            dodge_chance = Trait("Dodge Chance", static=True)
            dodge_chance.set_base(20) (no need to fill, because it is static)
            dodge_chance.current # returns 20

        Buff/Debuff a trait:
            This works for both static and dynamic traits.

            health = Trait("Health")
            health.set_base(100)
            health.fill()
            health.current # returns 100
            health.set_mod(-20)
            health.current # returns 100 if dynamic
            health.maximize()
            health.current # returns 80

        Dealing with multiple modifiers:
            health = Trait("Health")
            health.set_base(100)
            health.set_mod(100) # we get a +100 max health buff
            health.set_mod(health.get_mod() - 30) # we get a -30 health debuff
            health.maximize()
            health.current # returns 170
            health.set_mod(0) # clear all modifiers
            health.recover()
            health.current # returns 100
    """
    def __init__(
        self,
        name="",
        base=0,
        mod=0,
        static=False,
        **kwargs
    ):
        self.name = name.title()
        self.static = static
        self.data = {
            'base': base,
            'mod': mod,
            'current': base + mod
        }
        for key, value in kwargs.iteritems():
            self.data[key] = value

    def __str__(self):
        return "%s:\t\t%s" % (self.name, self.current)

    def __unicode__(self):
        return u"%s:\t\t%s" % (self.name, self.current)

    @property
    def base(self):
        return self.data['base']

    @base.setter
    def base(self, amount):
        if amount.isdigit():
            self.data['base'] = amount
        else:
            return False

    @property
    def current(self):
        return self.data['current']

    @current.setter
    def current(self, amount):
        if amount.isdigit():
            self.data['current'] = amount
        else:
            return False

    @property
    def mod(self):
        return self.data['mod']

    @mod.setter
    def mod(self, amount):
        if amount.isdigit():
            self.data['mod'] = amount
        else:
            return False

    def actual(self):
        return self.data['base'] + self.data['mod']

    def max(self):
        return self.actual

    def maximize(self):
        self.current = self.actual

    def fill(self):
        self.maximize()

    def recover(self):
        self.maximize()

    def fields(self):
        fields = []
        for field in self.data.keys():
            fields.append(field)
        return fields
