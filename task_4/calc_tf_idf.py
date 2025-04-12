import os
import re
import sys
import math

from bs4 import BeautifulSoup
import nltk


def get_all_words(directory: str):
    all_words = []
    for file in os.listdir(directory):
        if file[:6] == "tokens":
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                words = []
                for line in f:
                    word = line.strip()
                    words.append(word)
                all_words.append(words)
    return all_words


def get_count_containing_term(term: str, all_words) -> int:
    count = 0
    for words in all_words:
        if term in words:
            count += 1
    return count


def get_count_containing_lemma(tokens, all_words) -> int:
    count = 0
    for words in all_words:
        for token in tokens:
            if token in words:
                count += 1
                break
    return count


def main(
    term_directory: str, text_directory: str, output_directory: str, N: int
) -> None:

    all_words = get_all_words(term_directory)

    for filename in os.listdir(term_directory):
        file_number = filename[7:-4]
        text_filename = f"{file_number}.html"
        text_filepath = os.path.join(text_directory, text_filename)
        term_filepath = os.path.join(term_directory, filename)
        output_filepath = os.path.join(output_directory, f"{filename[:-4]}.txt")
        is_tokens = filename[:6] == "tokens"

        try:
            with open(text_filepath, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            tokenized_text = nltk.word_tokenize(text.lower())

            with open(output_filepath, "w+", encoding="utf-8") as result:
                with open(term_filepath, "r", encoding="utf-8") as terms:
                    if is_tokens:
                        for line in terms:
                            word = line.strip()
                            tf = tokenized_text.count(word) / len(tokenized_text)
                            idf = math.log(
                                N / get_count_containing_term(word, all_words)
                            )
                            result.write(f"{word} {idf} {tf*idf}\n")
                    else:
                        for line in terms:
                            lemma, tokens = line.split(":")
                            tf_lemma = 0

                            for token in tokens.split():
                                tf_lemma += tokenized_text.count(token) / len(
                                    tokenized_text
                                )

                            idf_lemma = math.log(
                                N
                                / get_count_containing_lemma(tokens.split(), all_words)
                            )

                            result.write(f"{lemma} {idf_lemma} {tf_lemma*idf_lemma}\n")

        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")


if __name__ == "__main__":
    term_directory_path = "../task_2/results"
    text_directory_path = "../task_1/results/pages"
    output_directory_path = "./results"

    if len(sys.argv) == 3:
        term_directory_path = sys.argv[1]
        text_directory_path = sys.argv[2]
    elif len(sys.argv) > 3:
        print("Ошибка, слишком много аргументов")
        exit(1)

    print(f"Ищем термины и леммы в директории {term_directory_path}")
    print(f"Ищем скачанные страницы в директории {text_directory_path}")
    print(f"Результат сохраним в {output_directory_path}")

    os.makedirs("results", exist_ok=True)
    main(term_directory_path, text_directory_path, output_directory_path, 150)
