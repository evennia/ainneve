from dataclasses import dataclass, field
from evennia import spawn

_NOT_FOUND = object()


@dataclass(frozen=True)
class PrototypeAttribute:
    attribute_name: str
    value: 'typing.Any'
    category: str
    locks: str


@dataclass(frozen=True)
class PrototypeDataClass:
    """
    An utility class for wrapping Prototypes

    Accessing Prototype attributes will work as if the value was directly set.
    If other properties of the attribute are desired, the underlying attributes dict
    will return the complete PrototypeAttribute Instance.
    """
    key: str
    typeclass: str
    prototype_key: str
    prototype_tags: list
    prototype_desc: str
    prototype_locks: str
    attributes: dict = field(default_factory=dict)
    aliases: list = field(default_factory=list)

    def __getattr__(self, item):
        attribute = self.attributes.get(item, _NOT_FOUND)
        if attribute is _NOT_FOUND:
            raise AttributeError()

        return attribute.value

    def has_attribute(self, key):
        if key in self.attributes:
            return True
        return False

    def get_attribute(self, key):
        return self.attributes.get(key)

    def spawn(self):
        return spawn(self.prototype_key).pop()


def convert_prototypes(prototypes):
    """
    Converts a dictionary of prototypes into a dictionary of PrototypeDataClass
    :param prototypes: A dictionary of prototypes
    :type prototypes: dict
    :rtype: dict
    """
    result = {}
    for prototype in prototypes.values():
        data_copy = prototype.copy()
        attrs = data_copy.pop('attrs')
        data_copy['attributes'] = {
            attribute[0]: PrototypeAttribute(attribute[0], attribute[1], attribute[2], attribute[3])
            for attribute in attrs
        }
        new_instance = PrototypeDataClass(**data_copy)
        result[new_instance.prototype_key] = new_instance

    return result
