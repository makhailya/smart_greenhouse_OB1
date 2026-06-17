# Changelog

## Добавлено тестирование (pytest)

- **Dev-зависимости:** pytest, pytest-cov
- **Конфиг:** `[tool.pytest.ini_options]` в pyproject.toml, `testpaths = ["tests"]`, `--cov=greenhouse`
- **Файлы:**
  - `tests/conftest.py` — фикстуры `db` и `controller` (temp-файлы БД, мок config.json)
  - `tests/test_database.py` — 6 тестов (создание таблиц, логи сенсоров/событий, лимит, порядок, пустой список)
  - `tests/test_controller.py` — 16 тестов (инициализация, `read_sensors`, управление поливом/вентиляцией/освещением через пороги, цикл `control()`)
- **Покрытие:** `controller.py` — 100%, `database.py` — 100%
- **Запуск:** `PYTHONPATH=. poetry run pytest`

## Исправления в `greenhouse/gui.py`

### 1. `_sensor_row` — метод помечен как `@staticmethod`
- **Файл:** `greenhouse/gui.py:77`
- **Проблема:** PyCharm: "Method '_sensor_row' may be 'static'" — метод не использует `self`
- **Изменение:** Добавлен декоратор `@staticmethod`, удалён параметр `self`

### 2. `_actuator_row` — метод помечен как `@staticmethod`
- **Файл:** `greenhouse/gui.py:87`
- **Проблема:** PyCharm: "Method '_actuator_row' may be 'static'" — метод не использует `self`
- **Изменение:** Добавлен декоратор `@staticmethod`, удалён параметр `self`

### 3. `root.after()` — подавлено ложное предупреждение PyCharm
- **Файл:** `greenhouse/gui.py:229`
- **Проблема:** PyCharm: "Parameter 'args' unfilled, expected '*tuple[]'" — typeshed-стабы tkinter используют `TypeVarTuple`/`Unpack` (PEP 646), который PyCharm не всегда корректно резолвит для bound-методов
- **Изменение:** Добавлен `# noinspection PyArgumentList` перед вызовом `after()`, так как это ложное срабатывание анализатора
