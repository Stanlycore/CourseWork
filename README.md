# Транслятор Python 2 → Python 3

## Описание

Полноценный транслятор кода с Python 2 на Python 3 с полной поддержкой синтаксиса и преобразований.

---

## Архитектура

```
Вход (Python 2) → ЛЕКСЕР → Токены → ПАРСЕР → AST → ГЕНЕРАТОР → Выход (Python 3)
```

---

## Основные компоненты

### Лексер (lexer/)
- Полная поддержка Python 2 токенов
- Обработка отступов INDENT/DEDENT
- Поддержка всех типов чисел (hex, binary, octal, float, exponential)
- **НОВОЕ**: DOT и <> оператор

### Парсер (parser/)
- Рекурсивный спуск
- Правильная приоритетность операторов
- **НОВОЕ**: Attribute (obj.attr) и Subscript (obj[index])
- **НОВОЕ**: Логические операторы (and, or, not)
- Полная обработка ошибок

### Генератор (generator/)
- Конвертация AST в Python 3 код
- Оптимальные скобки
- Все основные преобразования Python 2 → 3

---

## Поддерживаемые преобразования

| Python 2 | Python 3 |
|----------|----------|
| `print "Hello"` | `print("Hello")` |
| `x <> y` | `x != y` |
| `xrange(10)` | `range(10)` |
| `d.iteritems()` | `d.items()` |
| `raw_input()` | `input()` |
| `unicode()` | `str()` |
| `123L` | `123` |
| `obj.attr` | `obj.attr` |
| `obj[key]` | `obj[key]` |

Полная документация: [TRANSFORMATIONS.md](TRANSFORMATIONS.md)

---

## Структура проекта

```
CourseWork/
├── lexer/
│   ├── tokens.py
│   └── lexer.py
├── parser/
│   ├── ast_nodes.py       # НОВОЕ: Attribute, Subscript
│   └── parser.py
├── generator/
│   └── generator.py
├── examples/
│   └── all_features_examples.py  # 10 примеров + 2 ошибки
├── TRANSFORMATIONS.md
└── README.md
```

---

## Требования

- Python 3.9+
- Без внешних зависимостей

## Установка

```bash
git clone https://github.com/Stanlycore/CourseWork.git
cd CourseWork
git checkout new
```

---

## Примеры тестирования

В файле `examples/all_features_examples.py` находятся:
- **10 рабочих примеров** (все преобразования)
- **2 примера с ошибками** (обработка)
