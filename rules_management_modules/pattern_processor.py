# Set of functions for generating XPath from patterns
from lxml.etree import QName


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
