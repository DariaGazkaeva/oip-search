# DEMO

Поисковая система на основе векторного поиска по построенному индексу.

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

### 2. Запуск приложения

```
uvicorn main:app --reload
```
