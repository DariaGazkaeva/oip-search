from typing import Any
import os
import sys

from utils import find_element, lemmatize_term
from inverted_index import InvertedIndex, load_inverted_index


def find_parentheses(query: str) -> list[tuple[int, int]]:
    """
    Get indices for all parentheses on top level, e.g.
    for query = "(a OR h AND b OR (c and d)) OR NOT (e OR NOT f)"
    result will be [(0, 26), (35, 46)]
    """
    lst = []
    start_search = 0
    while True:
        ind = query.find("(", start_search)
        if ind == -1:
            return lst
        count = 1
        for i in range(ind + 1, len(query)):
            if query[i] == ")":
                count -= 1
            elif query[i] == "(":
                count += 1
            if count == 0:
                lst.append((ind, i))
                start_search = i + 1
                break
        if count > 0:
            raise ValueError(f"Incorrect parentheses: {query}")
    return lst


def validate_query_depth_1(query: list[str, Any]) -> bool:
    for i in range(len(query)):
        # validate OR and AND
        if query[i] in ["AND", "OR"]:
            if i == 0 or i == len(query) - 1:
                return False
            if query[i - 1] in ["AND", "OR", "NOT"]:
                return False
            if query[i + 1] in ["AND", "OR"]:
                return False

        # validate NOT
        elif query[i] == "NOT":
            if i == len(query) - 1:
                return False
            if query[i + 1] in ["AND", "OR"]:
                return False

        # validate subexpression
        else:
            if i < len(query) - 1 and query[i] in ["AND", "OR"]:
                return False

    return True


def parse_query(query: str) -> list[str, Any]:
    """
    Parse query to a list of terms, operators and sub-queries

    Args:
        query (str): _description_

    Returns:
        list[str, Any]: _description_
    """
    # top_level_parentheses: [(l_1, r_1), (l_2, r_2), ..., (l_n, r_n)]
    top_level_parentheses = find_parentheses(query)

    for i in range(len(top_level_parentheses) - 1, -1, -1):
        l, r = top_level_parentheses[i]
        sub_query = query[l + 1 : r]
        top_level_parentheses[i] = parse_query(sub_query)
        query = query[: l + 1] + query[r:]

    query_split = query.split()
    for i in range(len(query_split)):
        expression_or_operator = query_split[i]
        if expression_or_operator == "()":
            query_split[i] = top_level_parentheses.pop()

    if not validate_query_depth_1(query_split):
        raise ValueError(f"Incorrect query or subquery: {query}")
    return query_split


def run_query(
    parsed_query: list[str, Any] | str, inverted_index: InvertedIndex
) -> set[int]:
    if isinstance(parsed_query, str):
        return inverted_index.mapping[lemmatize_term(parsed_query)]

    for i in range(len(parsed_query)):
        if isinstance(parsed_query[i], list) or (
            isinstance(parsed_query[i], str)
            and parsed_query[i] not in ["AND", "OR", "NOT"]
        ):
            parsed_query[i] = run_query(parsed_query[i], inverted_index)

    while True:
        ind = find_element(parsed_query, "NOT")
        if ind == -1:
            break
        if parsed_query[ind + 1] == "NOT":
            parsed_query = parsed_query[:ind] + parsed_query[ind + 2 :]
            continue
        parsed_query[ind] = inverted_index.all_documents - parsed_query[ind + 1]
        parsed_query.pop(ind + 1)

    while True:
        ind = find_element(parsed_query, "AND")
        if ind == -1:
            break
        parsed_query[ind - 1] = parsed_query[ind - 1].intersection(
            parsed_query[ind + 1]
        )
        parsed_query = parsed_query[:ind] + parsed_query[ind + 2 :]

    while True:
        ind = find_element(parsed_query, "OR")
        if ind == -1:
            break
        parsed_query[ind - 1] = parsed_query[ind - 1].union(parsed_query[ind + 1])
        parsed_query = parsed_query[:ind] + parsed_query[ind + 2 :]

    assert (
        len(parsed_query) == 1
    ), f"Error: should have been single expression left, but got more: {parsed_query}"
    return parsed_query[0]


def boolean_search(query: str, inverted_index: InvertedIndex) -> list[int]:
    parsed_query = parse_query(query)
    results_set = run_query(parsed_query, inverted_index)
    return sorted(results_set)


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

    # print(parse_query_2("(a OR h AND b OR (c and d)) OR NOT (e OR NOT f)"))
    # print("матроид" in inverted_index.mapping.keys())
    # print(boolean_search_2("Матроид AND группа", inverted_index))
    # print(boolean_search("Матроид AND группа", inverted_index.mapping))
    # print(find_parentheses("(a or h AND b OR (c and d)) OR NOT (e OR not f)"))
    # print(boolean_search("(матрица)", inverted_index))
    # print(boolean_search("(матрица OR функция)", inverted_index))
    # print(
    #     boolean_search(
    #         "матрица OR функция AND (отображение OR NOT цезарь)", inverted_index
    #     )
    # )
