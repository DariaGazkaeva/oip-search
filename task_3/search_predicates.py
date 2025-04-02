from typing import Callable
import os
import sys

from inverted_index import InvertedIndex, load_inverted_index
from utils import lemmatize_term


def create_term_expression(term: str, inverted_index: InvertedIndex) -> Callable:
    lemma = lemmatize_term(term)

    def f(page_id):
        # print(lemma)
        return page_id in inverted_index.mapping[lemma]

    return f
    # return lambda page_id: page_id in inverted_index.mapping[lemma]


def create_not_expression(old: Callable) -> Callable:
    def f(page_id):
        # print(page_id)
        return not old(page_id)

    return f


def create_and_expression(left: Callable, right: Callable) -> Callable:
    def f(page_id):
        return left(page_id) and right(page_id)

    return f


def create_or_expression(left: Callable, right: Callable) -> Callable:
    def f(page_id):
        return left(page_id) or right(page_id)

    return f


def parse_query(query: str, inverted_index: InvertedIndex) -> list[Callable]:
    """Parse query to a list of predicates for page_id"""
    # if empty, return always True predicate
    if query == "":
        return lambda page_id: True

    # First, deal recursively with parentheses on top level
    top_parentheses_predicates = []
    top_parentheses_positions = []
    start_parentheses_search = 0
    while True:
        parentheses_start_index = query.find("(", start_parentheses_search)
        if parentheses_start_index == -1:
            break
        count = 1
        for i in range(parentheses_start_index + 1, len(query)):
            if query[i] == ")":
                count -= 1
            elif query[i] == "(":
                count += 1
            if count == 0:
                # found top level parentheses
                parentheses_predicate = parse_query(
                    query[parentheses_start_index + 1 : i], inverted_index
                )
                top_parentheses_predicates.append(parentheses_predicate)

                # change parentheses to simply "()"
                query = query[: parentheses_start_index + 1] + query[i:]

                top_parentheses_positions.append(parentheses_start_index)
                start_parentheses_search = parentheses_start_index + 2
                break
        if count > 0:
            raise ValueError(f"Incorrect parentheses: {query}")

    # then work with boolean operators in order of their priority

    query_split: list[str, Callable] = query.split()
    for i in range(len(query_split)):
        if query_split[i] == "()":
            query_split[i] = top_parentheses_predicates.pop()

    # NOT
    while True:
        try:
            ind = query_split.index("NOT")
        except ValueError:
            break
        if ind == len(query_split) - 1:
            raise ValueError(f"Incorrect query: {query}")
        expression = query_split[ind + 1]
        if expression == "NOT":
            query_split.pop(ind + 1)
            query_split.pop(ind)
            continue
        if isinstance(expression, str):
            expression = create_term_expression(expression, inverted_index)
        expression_not = create_not_expression(expression)
        query_split[ind] = expression_not
        query_split.pop(ind + 1)

    # AND
    while True:
        try:
            ind = query_split.index("AND")
        except ValueError:
            break
        if ind == 0 or ind == len(query_split) - 1:
            raise ValueError(f"Incorrect query: {query}")
        expression_left = query_split[ind - 1]
        if isinstance(expression_left, str):
            expression_left = create_term_expression(expression_left, inverted_index)
        expression_right = query_split[ind + 1]
        if isinstance(expression_right, str):
            expression_right = create_term_expression(expression_right, inverted_index)
        query_split[ind] = create_and_expression(expression_left, expression_right)
        query_split.pop(ind + 1)
        query_split.pop(ind - 1)

    # OR
    while True:
        try:
            ind = query_split.index("OR")
        except ValueError:
            break
        if ind == 0 or ind == len(query_split) - 1:
            raise ValueError(f"Incorrect query: {query}")
        expression_left = query_split[ind - 1]
        if isinstance(expression_left, str):
            expression_left = create_term_expression(expression_left, inverted_index)
        expression_right = query_split[ind + 1]
        if isinstance(expression_right, str):
            expression_right = create_term_expression(expression_right, inverted_index)
        query_split[ind] = create_or_expression(expression_left, expression_right)
        query_split.pop(ind + 1)
        query_split.pop(ind - 1)

    assert len(query_split) == 1, f"Incorrect query, {query_split}"
    expression = query_split[0]
    if isinstance(expression, str):
        expression = create_term_expression(expression, inverted_index)
    return expression


def boolean_search(query: str, inverted_index: InvertedIndex) -> list[int]:
    predicate = parse_query(query, inverted_index)
    all_pages = list(inverted_index.all_documents)
    return list(filter(predicate, all_pages))


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    inverted_index_file = "results/inverted_index.json"
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        inverted_index_file = sys.argv[1]
    else:
        print("Error, too many args")
        exit(1)

    inverted_index = load_inverted_index(inverted_index_file)
    print("Enter search query, e.g. `Матрица AND группа`")
    print("To quit, enter `exit`")
    print("If you want to search a page with word exit, use parentheses: `(exit)`")
    while True:
        query = input("Query: ")
        if query == "exit":
            exit(0)
        print(boolean_search(query, inverted_index))
