# NOTE: Input: XML concept, rule
from rules_management_modules import conditionals
from typing import List, Any


def selector_translation(selector) -> List[Any]:
    translation = []
    return translation


def pattern_match(element, selector) -> bool:
    # Default to False for failsafe
    match = False

    return match


def rules_engine(element, rule) -> bool:
    new_selector = selector_translation(rule['selector'])
    result = pattern_match(element, new_selector)
    return result

# NOTE: Output: Boolean||
