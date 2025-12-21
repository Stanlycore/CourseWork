# Семантический Анализатор

Модуль семантического анализа для транслятора Python 2 → Python 3.

## Овервью

Главная задача семантического анализатора — проверить корректность программы на смысловом уровне, т.e. те вещи, которые не могут быть обнаружены на этапе синтаксиса.

## Компоненты

### `errors.py`

Определения семантических ошибок.

**`ErrorType` enum:**

```python
class ErrorType(Enum):
    # Ошибки функций
    ARGUMENT_COUNT_MISMATCH      # Несовпадение количества аргументов
    DUPLICATE_ARGUMENT            # Дублирование названия аргумента
    RETURN_OUTSIDE_FUNCTION       # return вне функции
    YIELD_OUTSIDE_FUNCTION        # yield вне функции
    
    # Ошибки циклов
    BREAK_OUTSIDE_LOOP            # break вне цикла
    CONTINUE_OUTSIDE_LOOP         # continue вне цикла
    
    # Ошибки переменных
    UNDECLARED_IDENTIFIER         # использование необъявленной переменной
    REDEFINITION_BUILTIN          # переопределение встроенного
    
    # Ошибки констант
    CONST_DIVISION_BY_ZERO        # деление на ноль
    
    # Мертвый код
    DEAD_CODE                     # недостижимый код
```

**`SemanticError` класс:**

Представляет одну семантическую ошибку с точным локацирванием.

```python
class SemanticError:
    error_type: ErrorType
    message: str
    line: int
    column: int
```

### `semantic_analyzer.py`

Основная логика семантического анализатора.

#### `Scope` класс

Представляет область видимости с тракингом переменных и функций.

```python
class Scope:
    name: str                           # Название scope
    parent: Optional[Scope]             # Родительский scope
    declared_vars: Set[str]             # Объявленные переменные
    functions: Dict[str, FunctionDef]   # Определенные функции
    in_loop: bool                       # Находится ли внутри цикла
    in_function: bool                   # Находится ли внутри функции
```

#### `SemanticAnalyzer` класс

Основной числитель семантических ошибок.

**Основные методы:**

```python
def analyze(self, ast: ASTNode) -> List[SemanticError]:
    """Основной метод анализа"""
```

## Отвецаемые Ошибки

### 1. **ArgumentCountMismatch**

Обнаруживает несовпадение количества переданных аргументов функции.

```python
def foo(a, b):
    pass

foo(1)  # В функцию foo передано 1 аргумент, очидаются 2
```

### 2. **DuplicateArgument**

Обнаруживает дублированные кринг раметров в определении функции.

```python
def func(a, a):  # Не зарежистрировано в Питоне (SyntaxError), но проверим на данном этапе
    pass
```

### 3. **ReturnOutsideFunction**

Обнаруживает использование `return` вне тела функции.

```python
return 42  # Ошибка: return в глобальной области
```

### 4. **YieldOutsideFunction**

Обнаруживает использование `yield` вне тела функции.

```python
yield 1  # Ошибка: yield в глобальной области
```

### 5. **BreakOutsideLoop**

Обнаруживает использование `break` вне цикла.

```python
break  # Ошибка: break вне цикла
```

### 6. **ContinueOutsideLoop**

Обнаруживает использование `continue` вне цикла.

```python
continue  # Ошибка: continue вне цикла
```

### 7. **UndeclaredIdentifier**

Обнаруживает использование необъявленных переменных или функций.

```python
print(undefined_var)  # Ошибка: переменная undefined_var не объявлена
```

### 8. **RedefinitionBuiltin**

Обнаруживает переопределение встроенных типов и функций (Предупреждение).

```python
int = 5  # Предупреждение: переопределение встроенного типа
```

### 9. **ConstDivisionByZero**

Обнаруживает деление на ноль, когда делитель — константа.

```python
result = 42 / 0  # Ошибка: деление на константе 0
```

### 10. **DeadCode** (Planned)

Обнаруживает недостижимый код в структурах управления.

```python
def func():
    return 42
    print("This is unreachable")  # Предупреждение: недостижимый код
```

## Особенности и Носители

### Обработка Областей Видимости

Анализатор поддерживает іерархические структуры областей:

```
Глобальная область
  └─ Область функции
  └─ Область класса
      └─ Область метода
```

### Признание Встроенных

По умолчанию анализатор регистрирует все стандартные встроенные функции и типы в глобальном скопе, чтобы запретить основные использования.

## Примеры

### Пример 1: Ундеклейред Идентификатор

```python
def analyze_code(source):
    analyzer = SemanticAnalyzer()
    ast = parser.parse(source)  # from parser
    errors = analyzer.analyze(ast)
    
    for error in errors:
        print(error)  # Строка X:Y: [ERROR_TYPE] Мессаж
```

### Пример 2: Корректная программа

Код без семантических ошибок:

```python
def greet(name):
    greeting = "Hello, " + name
    print(greeting)
    return greeting

result = greet("Alice")
for i in range(5):
    print(i)
```

Анализатор не нарушит никаких ошибок.

## Интеграция в Поток Трансляции

В `main.py` семантический анализ этап 3 из 6:

```
[1/6] Лексический анализ
      ✓ Ок
[2/6] Синтаксический анализ
      ✓ Ок
[3/6] СЕМАНТИЧЕСКИЙ АНАЛИЗ  <-- ВЫПОЛНЯЕТСЯ ЗДЕСЬ
      ✓ Ок или ✗ ОШИБКИ
[4/6] Оптимизация
[5/6] Генерация кода
[6/6] Завершение
```
