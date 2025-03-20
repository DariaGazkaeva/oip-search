import os
import re
import sys

import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import pymorphy2


try:
    stopwords.words("russian")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.word_tokenize("test")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


def is_russian(word: str) -> bool:
    return bool(re.match(r"^[а-яё]+$", word, re.IGNORECASE))


def process_pages(directory: str) -> None:

    stop_words = set(stopwords.words("russian"))
    morph = pymorphy2.MorphAnalyzer()

    for filename in os.listdir(directory):
        file_number = filename[:-5]
        output_tokens_file = f"results/tokens_{file_number}.txt"
        output_lemma_file = f"results/lemmas_{file_number}.txt"

        tokens = set()
        lemma_to_tokens = {}

        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = nltk.word_tokenize(
                text.lower()
            )  # токенизация и приведение к нижнему регистру

            for word in words:
                # фильтрация (только из русских букв, не стоп-слова, без цифр, длиной больше 1)
                if (
                    is_russian(word)
                    and word not in stop_words
                    and not re.search(r"\d", word)
                    and len(word) > 1
                ):
                    tokens.add(word)

            # лемматизация
            for token in tokens:
                parsed_word = morph.parse(token)[0]
                lemma = parsed_word.normal_form
                if lemma not in lemma_to_tokens:
                    lemma_to_tokens[lemma] = set()
                lemma_to_tokens[lemma].add(token)

            # сохранение в файлы
            try:
                with open(output_tokens_file, "w+", encoding="utf-8") as f:
                    for token in tokens:
                        f.write(token + "\n")

                with open(output_lemma_file, "w+", encoding="utf-8") as f:
                    for lemma, token_set in lemma_to_tokens.items():
                        f.write(lemma + ": " + " ".join(token_set) + "\n")

                print(f"Токены сохранены в {output_tokens_file}")
                print(f"Лемматизированные токены сохранены в {output_lemma_file}")

            except Exception as e:
                print(f"Ошибка при сохранении файлов: {e}")

        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")


if __name__ == "__main__":
    directory_path = "../task_1/results/pages"
    if len(sys.argv) == 2:
        directory_path = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Ошибка, слишком много аргументов")
        exit(1)
    print(f"Ищем скачанные страницы в директории {directory_path}")
    os.makedirs("results", exist_ok=True)

    process_pages(directory_path)
