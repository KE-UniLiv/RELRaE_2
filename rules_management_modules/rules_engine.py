# NOTE: Input: XML concept, rule
from rules_management_modules import conditionals
from typing import List, Any
from lxml.etree import QName
import inspect


def pre_process_pattern(pattern):
    pp_pattern = list(map(list, pattern.items()))
    return pp_pattern


def process_pattern(element, pattern):
    # NOTE: This may be a little hacky but should work for now
    p_type = None

    # Find pattern type first
    for i in pattern:
        # print(pattern)
        if "pattern" in i:
            p_type = i[1]

    # TODO: Do necesarry collection
    # eg. for has_child find the correct child
    print(p_type)

    # NOTE: Maybe we handle conditionals last
    conds = [name for name, obj in inspect.getmembers(
        conditionals, inspect.isfunction)]
    for r in pattern:
        if r[0] in conds:
            print(f'-> {r[0]}: {r[1]}')

    return


def selector_translation(element, selector) -> List[Any]:
    translation = []
    for pattern in selector:
        selector_pattern = []
        pp = pre_process_pattern(pattern)
        process_pattern(element, pp)
        translation.append(selector_pattern)
    return translation


def pattern_match(element, selector) -> bool:
    # Default to False for failsafe
    match = False

    return match


def rules_engine(element, rule) -> bool:
    # xml_concept = schema.elements[QName(concept.name).localname]
    # xml_tag = xml_concept.elem.tag

    # print(f'element_type={QName(xml_tag).localname} name={
    #       QName(concept.name).localname} type={concept.type}')
    new_selector = selector_translation(element, rule['selector'])
    result = pattern_match(element, new_selector)
    return result

# NOTE: Output: Boolean|||
