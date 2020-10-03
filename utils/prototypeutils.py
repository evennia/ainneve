def create_attribute_dict(prototype):
    """
    Prototype dictionaries hold attributes in attrs, a list of tuples
    We convert this to a dictionary with names as keys and attribute value as a value

    :type prototype: dict
    :rtype: dict
    """
    attrs = prototype['attrs']
    attributes = {attribute[0]: attribute[1] for attribute in attrs}

    return attributes
