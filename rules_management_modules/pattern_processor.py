# Set of functions for generating XPath from patterns
from lxml.etree import QName
from xmlschema.validators import XsdAnyAttribute, XsdElement, XsdGroup


def elements_at_depth(elem, depth):
    if depth < 0:
        return []
    if depth == 0:
        return [elem]
    path = './' + '*/' * (depth-1) + '*'
    return elem.findall(path)


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
    match = False

    c_type = pattern[selector_index(pattern, 'child_type')][1]
    r_depth = pattern[selector_index(pattern, 'relative_depth')][1]

    descendents = elements_at_depth(element, r_depth)
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
