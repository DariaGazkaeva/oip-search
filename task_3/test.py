import os
import sys
from typing import Callable

from inverted_index import load_inverted_index, InvertedIndex
from search import boolean_search as boolean_search_main
from search_predicates import boolean_search as boolean_search_predicates


def test_case_1(inverted_index: InvertedIndex, document_lemmas: dict[int, list[str]]):
    query = "NOT (дифференциальный OR Интегральное) AND уравнение"
    print("*****")
    print(f'Testing query="{query}"')
    results_main = boolean_search_main(query, inverted_index)
    results_predicates = boolean_search_predicates(query, inverted_index)
    assert (
        results_main == results_predicates
    ), f"Two different results for query: {query}"

    for document_id, lemmas in document_lemmas.items():
        is_good = (
            not (("дифференциальный" in lemmas) or ("интегральный" in lemmas))
        ) and ("уравнение" in lemmas)
        is_in_results = document_id in results_main
        assert (
            is_good == is_in_results
        ), f"document_id={document_id}, is suitable for query: {is_good}, is found in results: {is_in_results}"

    print("Test case 1 is successful")
    print("*****")


def test_case_2(inverted_index: InvertedIndex, document_lemmas: dict[int, list[str]]):
    query = "(поле OR группы OR кольца) AND (матрицы OR базисы) AND NOT галуа"
    print("*****")
    print(f'Testing query="{query}"')
    results_main = boolean_search_main(query, inverted_index)
    results_predicates = boolean_search_predicates(query, inverted_index)
    assert (
        results_main == results_predicates
    ), f"Two different results for query: {query}"

    for document_id, lemmas in document_lemmas.items():
        is_good = (
            (("поле" in lemmas) or ("группа" in lemmas) or ("кольцо" in lemmas))
            and (("матрица" in lemmas) or ("базис" in lemmas))
            and ("галуа" not in lemmas)
        )
        is_in_results = document_id in results_main
        assert (
            is_good == is_in_results
        ), f"document_id={document_id}, is suitable for query: {is_good}, is found in results: {is_in_results}"

    print("Test case 2 is successful")
    print("*****")


def test_case_3(inverted_index: InvertedIndex, document_lemmas: dict[int, list[str]]):
    query = "NOT NOT (NOT (NOT механика))"
    print("*****")
    print(f'Testing query="{query}"')
    results_main = boolean_search_main(query, inverted_index)
    results_predicates = boolean_search_predicates(query, inverted_index)
    assert (
        results_main == results_predicates
    ), f"Two different results for query: {query}"

    for document_id, lemmas in document_lemmas.items():
        is_good = "механика" in lemmas
        is_in_results = document_id in results_main
        assert (
            is_good == is_in_results
        ), f"document_id={document_id}, is suitable for query: {is_good}, is found in results: {is_in_results}"

    print("Test case 3 is successful")
    print("*****")


def test_case_4(inverted_index: InvertedIndex, document_lemmas: dict[int, list[str]]):
    query = "Математики AND NOT Европы"
    print("*****")
    print(f'Testing query="{query}"')
    results_main = boolean_search_main(query, inverted_index)
    results_predicates = boolean_search_predicates(query, inverted_index)
    assert (
        results_main == results_predicates
    ), f"Two different results for query: {query}"

    for document_id, lemmas in document_lemmas.items():
        is_good = ("математика" in lemmas) and ("европа" not in lemmas)
        is_in_results = document_id in results_main
        assert (
            is_good == is_in_results
        ), f"document_id={document_id}, is suitable for query: {is_good}, is found in results: {is_in_results}"

    print("Test case 4 is successful")
    print("*****")


if __name__ == "__main__":
    inverted_index_file = "results/inverted_index.json"
    lemma_directory = "../task_2/results"
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        inverted_index_file = sys.argv[1]
    elif len(sys.argv) == 3:
        inverted_index_file = sys.argv[1]
        lemma_directory = sys.argv[1]
    else:
        print("Error, too many args")
        exit(1)
    inverted_index = load_inverted_index(inverted_index_file)

    document_lemmas = {}
    for filename in os.listdir(lemma_directory):
        if not filename.startswith("lemmas_"):
            continue
        try:
            document_id = int(filename[7:-4])
        except ValueError:
            print(f"Incorrect filename: {filename}, skipping")
            continue
        with open(os.path.join(lemma_directory, filename), "r", encoding="utf-8") as f:
            lines = f.readlines()
            lemmas = [line.split(":")[0] for line in lines]
        document_lemmas[document_id] = lemmas

    test_case_1(inverted_index, document_lemmas)
    test_case_2(inverted_index, document_lemmas)
    test_case_3(inverted_index, document_lemmas)
    test_case_4(inverted_index, document_lemmas)
