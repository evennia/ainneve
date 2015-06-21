class Trait:
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
        data={'current': 0, 'base': 0, 'mod': 0},
        static=False
    ):
        self.name = name.title()
        self.data = data
        self.static = static

    def __str__(self):
        return "%s:\t\t%s" % (self.name, self.current)

    def __unicode__(self):
        return u"%s:\t\t%s" % (self.name, self.current)

    @property
    def actual(self):
        return self.data["base"] + self.data["mod"]

    @property
    def current(self):
        if self.static:
            return self.actual
        else:
            return self.data["current"]

    @property
    def max(self):
        return self.actual

    @property
    def fields(self):
        fields = []
        for field in self.data.keys():
            fields.append(field)

        return fields

    def maximize(self):
        self.data["current"] = self.actual

    def fill(self):
        self.maximize()

    def recover(self):
        self.maximize()

    def get_base(self):
        return self.data["base"]

    def set_base(self, base=None):
        if base is None:
            return
        else:
            self.data["base"] = base

    def get_mod(self):
        return self.data["mod"]

    def set_mod(self, mod=None):
        if mod is None:
            return
        else:
            self.data["mod"] = mod

    def get_field(self, field=None):
        if field is None:
            return
        else:
            return self.data[field]

    def set_field(self, field=None, value=None):
        if field is None:
            return
        else:
            self.data[field] = value

    def delete_field(self, field=None):
        if (field not in [None, 'base', 'current', 'mod']):
            self.data.pop(field, None)
        else:
            return

    def add_field(self, field=None, value=None):
        if (field in self.data):
            return
        elif field is None:
            return
        else:
            self.data[field] = value
