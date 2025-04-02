from typing import Any

import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def find_element(lst: list, elem: Any) -> int:
    try:
        return lst.index(elem)
    except:
        return -1


def lemmatize_term(term: str) -> str:
    return morph.parse(term.lower())[0].normal_form
