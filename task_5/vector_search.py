import os
import sys
import string

import numpy as np
import pymorphy2


morph = pymorphy2.MorphAnalyzer()


def lemmatize_term(term: str) -> str:
    return morph.parse(term.lower())[0].normal_form


def parse_search_query(
    query: str, all_lemmas: list[str], lemma_idf: dict[str, float]
) -> list[float]:
    for char in string.punctuation:
        query = query.replace(char, " ")
    query_split = query.strip().split()
    query_split = [lemmatize_term(term) for term in query_split]

    tf = {}
    for lemma in query_split:
        if lemma in tf:
            tf[lemma] += 1
        else:
            tf[lemma] = 1

    for lemma in tf.keys():
        tf[lemma] = tf[lemma] / len(query_split)

    # if lemma is not present in search query => tf = 0
    # if lemma is not present in search index => idf = 0
    vector = [tf.get(lemma, 0) * lemma_idf.get(lemma, 0) for lemma in all_lemmas]
    return vector


def calc_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def get_similar_documents(
    query_vector: list[float], vectors: dict[int, list[float]], document_ids: np.ndarray
):
    similarity = np.array(
        [
            calc_cosine_similarity(query_vector, vectors[doc_id])
            for doc_id in document_ids
        ]
    )
    # minus for ascending order
    argsorted_similarity = np.argsort(-similarity)
    similarity = similarity[argsorted_similarity]
    sorted_document_ids = document_ids[argsorted_similarity]
    return sorted_document_ids, similarity


def load_tfidf(tfidf_dir: str):
    files = os.listdir(tfidf_dir)
    lemma_files = [file for file in files if file.startswith("lemmas_")]

    document_lemmas = {}  # dict: file index (int) -> dict: lemma(str) -> tfidf(float)
    lemma_idf = {}  # dict: lemma(str) -> idf(float)

    for file in lemma_files:
        doc_id = int(file[7:-4])
        document_lemmas[doc_id] = {}
        lines = [
            line.strip() for line in open(os.path.join(tfidf_dir, file)).readlines()
        ]
        for line in lines:
            lemma, idf, tfidf = line.split()
            idf = float(idf)
            tfidf = float(tfidf)
            document_lemmas[doc_id][lemma] = tfidf
            lemma_idf[lemma] = idf

    # build vectors now
    all_lemmas = list(lemma_idf.keys())
    all_lemmas.sort()  # for same results during different executions

    vectors = {}
    for doc_id, tfidf_dict in document_lemmas.items():
        vectors[doc_id] = [tfidf_dict.get(lemma, 0) for lemma in all_lemmas]

    return vectors, lemma_idf, all_lemmas


def load_index(index_file: str) -> dict[int, str]:
    lines = [line.strip().split() for line in open(index_file).readlines()]
    index = {int(id): url for id, url in lines}
    return index


if __name__ == "__main__":
    tfidf_dir = "../task_4/results"
    index_file = "../task_1/results/index.txt"
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        tfidf_dir = sys.argv[1]
    elif len(sys.argv) == 3:
        if sys.argv[1] != "-":
            tfidf_dir = sys.argv[1]
        index_file = sys.argv[2]
    else:
        print("Error, too many args")
        exit(1)

    index = load_index(index_file)
    vectors, lemma_idf, all_lemmas = load_tfidf(tfidf_dir)
    document_ids = np.array(list(vectors.keys()))

    print("Enter search query, e.g. `Матрицы над конечными полями Галуа`")
    print("To quit, enter `exit`")
    while True:
        query = input("Query: ").strip()
        if query == "exit":
            exit(0)
        query_vector = parse_search_query(query, all_lemmas, lemma_idf)

        sorted_document_ids, similarity = get_similar_documents(
            query_vector, vectors, document_ids
        )
        for top, doc_id in enumerate(sorted_document_ids[:5]):
            print(f"{top + 1}) (схожесть {round(similarity[top], 5)}) {index[doc_id]}")
