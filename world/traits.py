# -*- coding: utf-8 -*-
"""
Traits Module

`Trait` classes represent modifiable traits on objects or characters. They
are instantiated by a `TraitHandler` object, which is typically set up
as a property on the object or character's typeclass.

**Setup**
    To use traits on an object, add a function that passes the object
    itself into the constructor and returns a `TraitHandler`. This function
    should be decorated with the `lazy_property` decorator.

    If desired, multiple `TraitHandler` properties can be defined on one
    object. The optional `db_attribute` argument should be used to specify
    a different storage key for each `TraitHandler`. The default is `traits`.

Example:
    ```python
    from evennia.utils import lazy_property
    from world.traits import TraitHandler
        ...
    class Object(DefaultObject):
        ...
        @lazy_property
        def traits(self):
            return TraitHandler(self)
    ```

**Trait Configuration**
    `Trait` objects can be configured as one of three basic types with
    increasingly complex behavior.

    * Static - A simple trait model with a base value and optional modifier.

    * Counter - Trait with a base value and a modifiable current value that
        can vary along a range defined by optional min and max values.

    * Gauge - Modified counter type modeling a refillable "gauge".

    All traits have a read-only `actual` property that will report the trait's
    actual value.

    Example:

        ```python
        >>> hp = obj.traits.hp
        >>> hp.actual
        100
        ```

    They also support storing arbitrary data via either dictionary key or
    attribute syntax. Storage of arbitrary data in this way has the same
    constraints as any nested collection type stored in a persistent Evennia
    Attribute, so it is best to avoid attempting to store complex objects.

    Static Trait Configuration

        A static `Trait` stores a `base` value and a `mod` modifier value.
        The trait's actual value is equal to `base`+`mod`.

        Static traits can be used to model many different stats, such as
        Strength, Character Level, or Defense Rating in many tabletop gaming
        systems.

        Constructor Args:
            name (str): name of the trait
            type (str): 'static' for static traits
            base (int, float): base value of the trait
            mod Optional(int): modifier value
            extra Optional(dict): keys of this dict are accessible on the
                `Trait` object as attributes or dict keys

        Properties:
            actual (int, float): returns the value of `mod`+`base` properties
            extra (list[str]): list of keys stored in the extra data dict

        Methods:
            reset_mod(): sets the value of the `mod` property to zero

        Examples:

            '''python
            >>> strength = char.traits.str
            >>> strength.actual
            5
            >>> strength.mod = 2            # add a bonus to strength
            >>> str(strength)
            'Strength               7 (+2)'
            >>> strength.reset_mod()        # clear bonuses
            >>> str(strength)
            'Strength               5 (+0)'
            >>> strength.newkey = 'newvalue'
            >>> strength.extra
            ['newkey']
            >>> strength
            Trait({'name': 'Strength', 'type': 'trait', 'base': 5, 'mod': 0,
            'min': None, 'max': None, 'extra': {'newkey': 'newvalue'}})
            ```

    Counter Trait Configuration

        Counter type `Trait` objects have a `base` value similar to static
        traits, but adds a `current` value and a range along which it may
        vary. Modifier values are applied to this `current` value instead
        of `base` when determining the `actual` value. The `current` can
        also be reset to its `base` value by calling the `reset_counter()`
        method.

        Counter style traits are best used to represent game traits such as
        carrying weight, alignment points, a money system, or bonus/penalty
        counters.

        Constructor Args:
            (all keys listed above for 'static', plus:)
            min Optional(int, float, None): default None
                minimum allowable value for current; unbounded if None
            max Optional(int, float, None): default None
                maximum allowable value for current; unbounded if None

        Properties:
            actual (int, float): returns the value of `mod`+`current` properties

        Methods:
            reset_counter(): resets `current` equal to the value of `base`

        Examples:

            ```python
            >>> carry = caller.traits.carry
            >>> str(carry)
            'Carry Weight           0 ( +0)'
            >>> carry.current -= 3           # try to go negative
            >>> carry                        # enforces zero minimum
            'Carry Weight           0 ( +0)'
            >>> carry.current += 15
            >>> carry
            'Carry Weight          15 ( +0)'
            >>> carry.mod = -5               # apply a modifier to reduce
            >>> carry                        # apparent weight
            'Carry Weight:         10 ( -5)'
            >>> carry.current = 10000        # set a semi-large value
            >>> carry                        # still have the modifier
            'Carry Weight        9995 ( -5)'
            >>> carry.reset()                # remove modifier
            >>> carry
            'Carry Weight        10000 ( +0)'
            >>> carry.reset_counter()
            >>> +carry
            0
            ```

    Gauge Trait Configuration

        A gauge type `Trait` is a modified counter trait used to model a
        gauge that can be emptied and refilled. The `base` property of a
        gauge trait represents its "full" value. The `mod` property increases
        or decreases that "full" value, rather than the `current`.

        By default gauge type traits have a `min` of zero, and a `max` set
        to the `base`+`mod` properties. A gauge will still work if its `max`
        property is set to a value above its `base` or to None.

        Gauge type traits are best used to represent traits such as health
        points, stamina points, or magic points.

        Constructor Args:
            (all keys listed above for 'static', plus:)
            min Optional(int, float, None): default 0
                minimum allowable value for current; unbounded if None
            max Optional(int, float, None, 'base'): default 'base'
                maximum allowable value for current; unbounded if None;
                if 'base', returns the value of `base`+`mod`.

        Properties:
            actual (int, float): returns the value of the `current` property

        Methods:
            fill_gauge(): adds the value of `base`+`mod` to `current`
            percent(): returns the ratio of actual value to max value as
                a percentage. if `max` is unbound, return the ratio of
                `current` to `base`+`mod` instead.

        Examples:

            ```python
            >>> hp = caller.traits.hp
            >>> repr(hp)
            GaugeTrait({'name': 'HP', 'type': 'gauge', 'base': 10, 'mod': 0,
            'min': 0, 'max': 'base', 'current': 10, 'extra': {}})
            >>> str(hp)
            'HP:           10 /   10 ( +0)'
            >>> hp.current -= 6                    # take damage
            >>> str(hp)
            'HP:            4 /   10 ( +0)'
            >>> hp.current -= 6                    # take damage to below min
            >>> str(hp)
            'HP:            0 /   10 ( +0)'
            >>> hp.fill()                          # refill trait
            >>> str(hp)
            'HP:           10 /   10 ( +0)'
            >>> hp.current = 15                    # try to set above max
            >>> str(hp)                            # disallowed because max=='actual'
            'HP:           10 /   10 ( +0)'
            >>> hp.mod += 3                        # bonus on full trait
            >>> str(hp)                            # buffs flow to current
            'HP:           13 /   13 ( +3)'
            >>> hp.current -= 5
            >>> str(hp)
            'HP:            8 /   13 ( +3)'
            >>> hp.reset()                         # remove bonus on reduced trait
            >>> str(hp)                            # debuffs do not affect current
            'HP:            8 /   10 ( +0)'
            ```
"""

from evennia.utils.dbserialize import _SaverDict
from evennia.utils import logger, lazy_property
from functools import total_ordering

TRAIT_TYPES = ('static', 'counter', 'gauge')
RANGE_TRAITS = ('counter', 'gauge')


class TraitException(Exception):
    """Base exception class raised by `Trait` objects.

    Args:
        msg (str): informative error message
    """
    def __init__(self, msg):
        self.msg = msg


class TraitHandler(object):
    """Factory class that instantiates Trait objects.

    Args:
        obj (Object): parent Object typeclass for this TraitHandler
        db_attribute (str): name of the DB attribute for trait data storage
    """
    def __init__(self, obj, db_attribute='traits'):
        if not obj.attributes.has(db_attribute):
            obj.attributes.add(db_attribute, {})

        self.attr_dict = obj.attributes.get(db_attribute)
        self.cache = {}

    def __len__(self):
        """Return number of Traits in 'attr_dict'."""
        return len(self.attr_dict)

    def __setattr__(self, key, value):
        """Returns error message if trait objects are assigned directly."""
        if key in ('attr_dict', 'cache'):
            super(TraitHandler, self).__setattr__(key, value)
        else:
            raise TraitException(
                "Trait object not settable. Assign one of "
                "`{0}.base`, `{0}.mod`, or `{0}.current` ".format(key) +
                "properties instead."
            )

    def __setitem__(self, key, value):
        """Returns error message if trait objects are assigned directly."""
        return self.__setattr__(key, value)

    def __getattr__(self, trait):
        """Returns Trait instances accessed as attributes."""
        return self.get(trait)

    def __getitem__(self, trait):
        """Returns `Trait` instances accessed as dict keys."""
        return self.get(trait)

    def get(self, trait):
        """
        Args:
            trait (str): key from the traits dict containing config data
                for the trait. "all" returns a list of all trait keys.

        Returns:
            (`Trait` or `None`): named Trait class or None if trait key
            is not found in traits collection.
        """
        if trait not in self.cache:
            if trait not in self.attr_dict:
                return None
            data = self.attr_dict[trait]
            self.cache[trait] = Trait(data)
        return self.cache[trait]

    def add(self, key, name, type='static',
            base=0, mod=0, min=None, max=None, extra={}):
        """Create a new Trait and add it to the handler."""
        if key in self.attr_dict:
            raise TraitException("Trait '{}' already exists.".format(key))

        if type in TRAIT_TYPES:
            trait = dict(name=name,
                         type=type,
                         base=base,
                         mod=mod,
                         extra=extra)
            if min:
                trait.update(dict(min=min))
            if max:
                trait.update(dict(max=max))

            self.attr_dict[key] = trait
        else:
            raise TraitException("Invalid trait type specified.")

    def remove(self, trait):
        """Remove a Trait from the handler's parent object."""
        if trait not in self.attr_dict:
            raise TraitException("Trait not found: {}".format(trait))

        if trait in self.cache:
            del self.cache[trait]
        del self.attr_dict[trait]

    def clear(self):
        """Remove all Traits from the handler's parent object."""
        for trait in self.all:
            self.remove(trait)

    @property
    def all(self):
        """Return a list of all trait keys in this TraitHandler."""
        return self.attr_dict.keys()


@total_ordering
class Trait(object):
    """Represents an object or Character trait.

    Note:
        See module docstring for configuration details.
    """
    def __init__(self, data):
        if not 'name' in data:
            raise TraitException(
                "Required key not found in trait data: 'name'")
        if not 'type' in data:
            raise TraitException(
                "Required key not found in trait data: 'type'")
        self._type = data['type']
        if not 'base' in data:
            data['base'] = 0
        if not 'mod' in data:
            data['mod'] = 0
        if not 'extra' in data:
            data['extra'] = {}
        if 'min' not in data:
            data['min'] = 0 if self._type == 'gauge' else None
        if 'max' not in data:
            data['max'] = 'base' if self._type == 'gauge' else None

        self._data = data
        self._keys = ('name', 'type', 'base', 'mod',
                      'current', 'min', 'max', 'extra')
        self._locked = True

        if not isinstance(data, _SaverDict):
            logger.log_warn(
                'Non-persistent {} class loaded.'.format(
                    type(self).__name__
                ))

    def __repr__(self):
        """Debug-friendly representation of this Trait."""
        return "{}({{{}}})".format(
            type(self).__name__,
            ', '.join(["'{}': {!r}".format(k, self._data[k])
                for k in self._keys if k in self._data]))

    def __str__(self):
        """User-friendly string representation of this `Trait`"""
        if self._type == 'gauge':
            status = "{actual:4} / {base:4}".format(
                actual=self.actual,
                base=self.base)
        else:
            status = "{actual:11}".format(actual=self.actual)

        return "{name:12} {status} ({mod:+3})".format(
            name=self.name,
            status=status,
            mod=self.mod)

    def __unicode__(self):
        """User-friendly unicode representation of this `Trait`"""
        return unicode(str(self))

    # Extra Properties magic

    def __getitem__(self, key):
        """Access extra parameters as dict keys."""
        try:
            return self.__getattr__(key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """Set extra parameters as dict keys."""
        self.__setattr__(key, value)

    def __delitem__(self, key):
        """Delete extra prameters as dict keys."""
        self.__delattr__(key)

    def __getattr__(self, key):
        """Access extra parameters as attributes."""
        if key in self._data['extra']:
            return self._data['extra'][key]
        else:
            raise AttributeError(
                "{} '{}' has no attribute {!r}".format(
                    type(self).__name__, self.name, key
                ))

    def __setattr__(self, key, value):
        """Set extra parameters as attributes.

        Arbitrary attributes set on a Trait object will be
        stored in the 'extra' key of the `_data` attribute.

        This behavior is enabled by setting the instance
        variable `_locked` to True.
        """
        propobj = getattr(self.__class__, key, None)
        if isinstance(propobj, property):
            if propobj.fset is None:
                raise AttributeError("can't set attribute")
            propobj.fset(self, value)
        else:
            if (self.__dict__.get('_locked', False) and
                    key not in ('_keys',)):
                self._data['extra'][key] = value
            else:
                super(Trait, self).__setattr__(key, value)

    def __delattr__(self, key):
        """Delete extra parameters as attributes."""
        if key in self._data['extra']:
            del self._data['extra'][key]

    # Numeric operations magic

    def __eq__(self, other):
        """Support equality comparison between Traits or Trait and numeric.

        Note:
            This class uses the @functools.total_ordering() decorator to
            complete the rich comparison implementation, therefore only
            `__eq__` and `__lt__` are implemented.
        """
        if type(other) == Trait:
            return self.actual == other.actual
        elif type(other) in (float, int):
            return self.actual == other
        else:
            return NotImplemented

    def __lt__(self, other):
        """Support less than comparison between `Trait`s or `Trait` and numeric."""
        if isinstance(other, Trait):
            return self.actual < other.actual
        elif type(other) in (float, int):
            return self.actual < other
        else:
            return NotImplemented

    def __pos__(self):
        """Access `actual` property through unary `+` operator."""
        return self.actual

    def __add__(self, other):
        """Support addition between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return self.actual + other.actual
        elif type(other) in (float, int):
            return self.actual + other
        else:
            return NotImplemented

    def __sub__(self, other):
        """Support subtraction between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return self.actual - other.actual
        elif type(other) in (float, int):
            return self.actual - other
        else:
            return NotImplemented

    def __mul__(self, other):
        """Support multiplication between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return self.actual * other.actual
        elif type(other) in (float, int):
            return self.actual * other
        else:
            return NotImplemented

    def __floordiv__(self, other):
        """Support floor division between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return self.actual // other.actual
        elif type(other) in (float, int):
            return self.actual // other
        else:
            return NotImplemented

    # yay, commutative property!
    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        """Support subtraction between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return other.actual - self.actual
        elif type(other) in (float, int):
            return other - self.actual
        else:
            return NotImplemented

    def __rfloordiv__(self, other):
        """Support floor division between `Trait`s or `Trait` and numeric"""
        if isinstance(other, Trait):
            return other.actual // self.actual
        elif type(other) in (float, int):
            return other // self.actual
        else:
            return NotImplemented

    # Public members

    @property
    def name(self):
        """Display name for the trait."""
        return self._data['name']

    @property
    def actual(self):
        """The "actual" value of the trait."""
        if self._type == 'gauge':
            return self.current
        elif self._type == 'counter':
            return self._mod_current()
        else:
            return self._mod_base()

    @property
    def base(self):
        """The trait's base value.

        Note:
            The setter for this property will enforce any range bounds set
            on this `Trait`.
        """
        return self._data['base']

    @base.setter
    def base(self, amount):
        if self._data.get('max', None) == 'base':
            self._data['base'] = amount
        if type(amount) in (int, float):
            self._data['base'] = self._enforce_bounds(amount)

    @property
    def mod(self):
        """The trait's modifier."""
        return self._data['mod']

    @mod.setter
    def mod(self, amount):
        if type(amount) in (int, float):
            delta = amount - self._data['mod']
            self._data['mod'] = amount
            if self._type == 'gauge':
                if delta >= 0:
                    # apply increases to current
                    self.current = self._enforce_bounds(self.current + delta)
                else:
                    # but not decreases, unless current goes out of range
                    self.current = self._enforce_bounds(self.current)

    @property
    def min(self):
        """The lower bound of the range."""
        if self._type in RANGE_TRAITS:
            return self._data['min']
        else:
            raise AttributeError(
                "static 'Trait' object has no attribute 'min'.")

    @min.setter
    def min(self, amount):
        if self._type in RANGE_TRAITS:
            if amount is None: self._data['min'] = amount
            elif type(amount) in (int, float):
                self._data['min'] = amount if amount < self.base else self.base
        else:
            raise AttributeError(
                "static 'Trait' object has no attribute 'min'.")

    @property
    def max(self):
        """The maximum value of the `Trait`.

        Note:
            This property may be set to the string literal 'base'.
            When set this way, the property returns the value of the
            `mod`+`base` properties.
        """
        if self._type in RANGE_TRAITS:
            if self._data['max'] == 'base':
                return self._mod_base()
            else:
                return self._data['max']
        else:
            raise AttributeError(
                "static 'Trait' object has no attribute 'max'.")

    @max.setter
    def max(self, value):
        if self._type in RANGE_TRAITS:
            if value == 'base' or value is None:
                self._data['max'] = value
            elif type(value) in (int, float):
                self._data['max'] = value if value > self.base else self.base
        else:
            raise AttributeError(
                "static 'Trait' object has no attribute 'max'.")

    @property
    def current(self):
        """The `current` value of the `Trait`."""
        if self._type == 'gauge':
            return self._data.get('current', self._mod_base())
        else:
            return self._data.get('current', self.base)

    @current.setter
    def current(self, value):
        if self._type in RANGE_TRAITS:
            if type(value) in (int, float):
                self._data['current'] = self._enforce_bounds(value)
        else:
            raise AttributeError(
                "'current' property is read-only on static 'Trait'.")

    @property
    def extra(self):
        """Returns a list containing available extra data keys."""
        return self._data['extra'].keys()

    def reset_mod(self):
        """Clears any mod value on the `Trait`."""
        self.mod = 0

    def reset_counter(self):
        """Resets `current` property equal to `base` value."""
        self.current = self.base

    def fill_gauge(self):
        """Adds the `mod`+`base` to the `current` value.

        Note:
            Will honor the upper bound if set.
        """
        self.current = \
            self._enforce_bounds(self.current + self._mod_base())

    def percent(self):
        """Returns the value formatted as a percentage."""
        if self._type in RANGE_TRAITS:
            if self.max:
                return "{:3.1f}%".format(self.current * 100.0 / self.max)
            elif self._type == 'counter' and self.base != 0:
                return "{:3.1f}%".format(self.current * 100.0 / self._mod_base())
            elif self._type == 'gauge' and self._mod_base() != 0:
                return "{:3.1f}%".format(self.current * 100.0 / self._mod_base())
        # if we get to this point, it's either a static trait or
        # a divide by zero situation
        return "100.0%"

    # Private members

    def _mod_base(self):
        return self._enforce_bounds(self.mod + self.base)

    def _mod_current(self):
        return self._enforce_bounds(self.mod + self.current)

    def _enforce_bounds(self, value):
        """Ensures that incoming value falls within trait's range."""
        if self._type in RANGE_TRAITS:
            if self.min is not None and value <= self.min:
                return self.min
            if self._data['max'] == 'base' and value >= self.mod + self.base:
                return self.mod + self.base
            if self.max is not None and value >= self.max:
                return self.max
        return value

