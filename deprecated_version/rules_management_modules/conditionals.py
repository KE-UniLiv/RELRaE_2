def has_attribute(element, attribute) -> bool:
    if attribute in list(element.attributes.keys()):
        return True
    return False
