# Task 3. Индекс и булев поиск

Скрипты на Python для получения инвертированного списка термина и булева поиска по запросу.

## Участники
- 11-101 Калимуллин Ильяс  
- 11-101 Газкаева Дарья

## Запуск
### 1. Установите зависимости.

Для этого рекомендуем сначала создать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate
```
Если на `Windows`, то 
```
python -m venv .venv
.\.venv\Scripts\activate
```

Далее установите зависимости
```bash
pip install -r requirements.txt
```

### 2. Запуск скрипта для создания индекса

```python
python inverted_index.py <path_to_save_index> <path_to_lemmas_dir>
```
Необязательные аргументы:
- `path_to_save_index` — путь для сохранения индекса, по умолчанию `results/inverted_index.json`
- `path_to_lemmas_dir` — путь до директории с файлами с леммами для каждой страницы
**Важно**: в директории могут быть и другие файлы, но файлы с леммами должны называться в формате `lemmas_{номер}.txt`

### 3. Булев поиск

Реализованы два алгоритма: основной и через предикаты. Оба алгоритма работают с одинаковым результатом
```python
python search.py <path_to_index>
```
или же
```python
python search_predicate.py <path_to_index>
```
`path_to_index` — необязательный аргумент, путь до сохраненного индекса, по умолчанию `results/inverted_index.json`

#### Основной алгоритм vs алгоритм через предикаты
В основном варианте поиска происходят операции со множествами (`sets`) в Python: их объединение и пересечение.

В варианте с предикатами последовательно строится функция-предикат, которая является фильтром для документа (по его `id`).
Функция строится через последовательную композицию от нижних к верхним уровням выражения.

Насколько нам известно, оба варианта работают одинаково

### 4. Тесты

Мы создали несколько тест-кейсов для демонстрации решения. Запустить их можно так:
```python
python test.py <path_to_index> <path_to_lemmas_dir>
```
Аргументы опциональны и аналогичны аргументам для создания индекса
