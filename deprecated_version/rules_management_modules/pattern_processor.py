# Set of functions for generating XPath from patterns
from lxml.etree import QName
from xmlschema.validators import XsdAnyAttribute, XsdElement, XsdGroup, XsdComplexType


def elements_at_depth(elem, depth):
    if depth < 0:
        return []
    if depth == 0:
        return [elem]
    path = './' + '*/' * (depth-1) + '*'
    return elem.findall(path)


def elements(xsd_element):
    t = xsd_element.type
    if not t.is_complex() or t.content is None:
        return []
    return list(t.content.iter_elements())


def selector_index(selector, attribute):
    for r in selector:
        if attribute in r:
            return (selector.index(r))


def has_choice(element, pattern):
    candidates = []

    group = element.type.model_group or element.type.content
    if not isinstance(group, XsdGroup):
        return candidates

    def walk(component, choice_seen):
        if isinstance(component, XsdElement):
            return choice_seen
        if isinstance(component, XsdGroup):
            # print(component.model)
            # print(component.model == 'choice')
            choice_seen = choice_seen or (component.model == 'choice')
            for item in component:
                if walk(item, choice_seen):
                    return True
        return False

    if not walk(group, False):
        return candidates
    else:
        pot_candidates = has_child(element, pattern)

    for c in pot_candidates:
        parent = c.parent
        if isinstance(parent, XsdGroup) and parent.model == 'choice':
            candidates.append(c)

    return candidates


def has_child(element, pattern):
    candidates = []

    c_type = pattern[selector_index(pattern, 'child_type')][1]
    # r_depth = pattern[selector_index(pattern, 'relative_depth')][1]

    descendents = elements(element)
    for d in descendents:
        if type(d.type).__name__ == c_type:
            candidates.append(d)

    return candidates


def has_attribute(element, pattern):
    candidates = []

    if pattern[selector_index(pattern, 'attribute')][1] != 'All':
        att = []
        att.append(pattern[selector_index(pattern, 'attribute')][1])
    else:
        att = []
        try:
            for a in element.attributes.values():
                att.append(a)
        except Exception:
            for a in element.values():
                att.append(a)

    for a in att:
        if isinstance(a, str):
            if getattr(element, a, None):
                candidates.append(element)
        else:
            if isinstance(a, XsdAnyAttribute):
                continue
            candidates.append(a)

    return candidates


def has_min_occurs(element, pattern):
    candidates = []
    has_children = has_child(element, pattern)

    if not has_children:
        return candidates
    else:
        for c in has_children:
            if c.occurs is not None:
                candidates.append(c)
    return candidates


def has_max_occurs(element, pattern):
    candidates = []
    has_children = has_child(element, pattern)

    if not has_child:
        return candidates
    else:
        for c in has_children:
            if c.occurs is not None:
                if c.occurs[1] is None:
                    continue
                candidates.append(c)
    return candidates


def has_required_attribute(element, pattern):
    candidates = []
    has_attributes = has_attribute(element, pattern)

    if not has_attributes:
        return candidates
    else:
        for a in has_attributes:
            if a.use == 'required':
                candidates.append(a)
    return candidates

def global_is_complex(xsd_element):
    schema = xsd_element.schema
    qname = xsd_element.qualified_name

    # Check if a global element with same name exists
    global_elem = schema.maps.elements.get(qname)
    if global_elem is None:
        return False

    # Check if its type is complex
    return isinstance(global_elem.type, XsdComplexType)

# TODO: Populate Function
def has_new_child(element, pattern):
    candidates = []

    c_type = pattern[selector_index(pattern, 'child_type')][1]

    descendents = elements(element)
    for d in descendents:
        if type(d).__name__ == c_type:
            # NOTE: Check if element is defined anywhere else in the schema
            if not global_is_complex(d):
                candidates.append(d)
                print(d)

    return candidates

# TODO: Populate Function
def has_existing_child(element, pattern):
    candidates = []

    c_type = pattern[selector_index(pattern, 'child_type')][1]

    descendents = elements(element)
    for d in descendents:
        if type(d).__name__ == c_type:
            if global_is_complex(d):
                candidates.append(d)
                print(d)

    return candidates
