# Task 4. TF-IDF

Скрипты на Python для подсчета TF-IDF.

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

### 2. Запуск скрипта

```python
python calc_tf_idf.py <path_to_dir_with_terms> <path_to_dir_with_pages>
```
Необязательные аргументы:
- `path_to_dir_with_terms` — путь до директории, где лежат токены и леммы, по умолчанию `../task_2/results`
- `path_to_dir_with_pages` — путь до директории, где лежат сами страницы, по умолчанию `../task_1/results/pages`
**Важно**: файлы с токенами и леммами должны называться в формате `tokens_{номер}.txt` и `lemmas_{номер}.txt`, файлы страниц должны называться в формате `{номер}.html`

Результаты подсчета TF-IDF будут лежать в директории `./results`
