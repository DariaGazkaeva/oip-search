import os
import pathlib
import sys
import json


class InvertedIndex:
    def __init__(self, mapping: dict[str, set[int]], all_documents: set[int]):
        self.mapping = mapping
        self.all_documents = all_documents

        if not isinstance(self.all_documents, set):
            self.all_documents = set(self.all_documents)

        for k, v in self.mapping.items():
            if not isinstance(v, set):
                self.mapping[k] = set(v)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, InvertedIndex):
            return {"all_documents": obj.all_documents, "mapping": obj.mapping}
        return json.JSONEncoder.default(self, obj)


def save_inverted_index(inverted_index: InvertedIndex, path: str) -> None:
    path = pathlib.Path(path)
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w+") as f:
        json.dump(inverted_index, f, cls=SetEncoder, ensure_ascii=False)


def load_inverted_index(path: str) -> None:
    with open(path, "r") as f:
        args = json.load(f)
        return InvertedIndex(**args)


def build_inverted_index(lemma_directory: str) -> InvertedIndex:
    inverted_index = {}
    all_documents = set()
    for filename in os.listdir(lemma_directory):
        if not filename.startswith("lemmas_"):
            continue
        try:
            document_id = int(filename[7:-4])
        except ValueError:
            print(f"Incorrect filename: {filename}, skipping")
            continue
        all_documents.add(document_id)
        with open(os.path.join(lemma_directory, filename), "r", encoding="utf-8") as f:
            lines = f.readlines()
            lemmas = [line.split(":")[0] for line in lines]

        for lemma in lemmas:
            if lemma not in inverted_index:
                inverted_index[lemma] = set()
            inverted_index[lemma].add(document_id)

    return InvertedIndex(mapping=inverted_index, all_documents=all_documents)


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
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

    inverted_index = build_inverted_index(lemma_directory)
    save_inverted_index(inverted_index, inverted_index_file)
    print("Created index! Location:", inverted_index_file)
