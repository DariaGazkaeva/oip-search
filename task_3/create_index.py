import os
import re


def build_inverted_index(directory, inverted_index_file):
    inverted_index = {}
    for filename in os.listdir(directory):
        try:
            document_id = int(filename[7:-4])
        except ValueError:
            print(f"Некорректное имя файла: {filename}, файл пропущен")
            continue

        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            text = f.read().lower()
            terms = re.findall(r"\b\w+\b", text)

        for term in terms:
            if term not in inverted_index:
                inverted_index[term] = set()
            inverted_index[term].add(document_id)

    # сохранение в файл
    with open(inverted_index_file, "w+") as f:
        for term in inverted_index:
            f.write(term + ": " + " ".join(str(s) for s in inverted_index[term]) + "\n")

    return inverted_index
