# NOTE: Input: XML concept, rule
from rules_management_modules import conditionals
from rules_management_modules import pattern_processor
from typing import List, Any
from lxml.etree import QName
import inspect


def get_elem_name(concept):
    xml_concept = QName(concept.name).localname
    return xml_concept


def pre_process_pattern(pattern):
    pp_pattern = list(map(list, pattern.items()))
    return pp_pattern


def process_pattern(element, pattern):
    # NOTE: This may be a little hacky but should work for now
    p_type = "Unknown"
    found = []

    # NOTE: Not needed
    id = ""
    for r in pattern:
        if "id" in r:
            id = r[1]

    # Find pattern type first
    for i in pattern:
        if "pattern" in i:
            p_type = i[1]

    p_parse = getattr(pattern_processor, p_type)
    candidates = p_parse(element, pattern)

    # Maybe I don't need this list
    # patterns = [name for name, obj in inspect.getmembers(xpath_processors, inspect.isfunction)]

    # NOTE: Maybe we handle conditionals last
    cond_funcs = [name for name, obj in inspect.getmembers(
        conditionals, inspect.isfunction)]
    conds = []
    for r in pattern:
        if r[0] in cond_funcs:
            # FIX: Swap out "id" for element object
            # Maybe this should be done in post after the Xpath is processed
            # These indecies are relied on even though they are redundant
            cond = [id, r[0], r[1]]
            conds.append(cond)
            # print(f'->  {cond}')

    for c in candidates:
        over_valid = True
        for cond in conds:
            test = getattr(conditionals, cond[1])
            valid = test(c, cond[2])
            # print(valid)
            if not valid:
                over_valid = False
        if over_valid:
            found.append(c)

    # print(found)

    return found


def selector_translation(element, selector) -> List[Any]:
    translation = []
    # print(get_elem_name(element))
    for pattern in selector:
        pp = pre_process_pattern(pattern)
        translation.append(process_pattern(element, pp))
    print('')
    return translation


def rules_engine(element, rule):
    if type(element.type).__name__ != rule['element_type']:
        return False, None
    if 'selector' in rule:
        candidates = selector_translation(element, rule['selector'])
    else:
        candidates = [[""]]
    result = list(set(candidates[0]).intersection(*candidates[1:]))
    if not result:
        return False, None
    return True, result

# NOTE: Output: Boolean
