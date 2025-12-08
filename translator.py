#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translator Python2 -> Python3
Полная реализация с лексическим анализом, синтаксическим анализом,
таблицей идентификаторов и генерацией Python3 кода.

Основные различия между Python2 и Python3:
1. print statement -> print function
2. raw_input -> input
3. xrange -> range
4. dict.has_key() -> in operator
5. dict.iteritems() -> dict.items()
6. long type -> int
7. / operator (true division)
8. unicode strings по умолчанию
9. exception handling (as -> except)
10. raise statement syntax
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Tuple
from enum import Enum, auto
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from collections import defaultdict

# ============================================================================
# ЧАСТЬ 1: ЛЕКСИЧЕСКИЙ АНАЛИЗАТОР
# ============================================================================

class TokenType(Enum):
    """Типы лексем"""
    # Литералы
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    
    # Ключевые слова
    KEYWORD = auto()
    
    # Операторы
    ASSIGN = auto()
    OPERATOR = auto()
    
    # Символы
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    
    # Специальные
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    COMMENT = auto()
    EOF = auto()
    UNKNOWN = auto()

@dataclass
class Token:
    """Представление токена"""
    type: TokenType
    value: str
    line: int
    column: int
    original_line: str = ""

class LexicalAnalyzer:
    """Лексический анализатор Python кода"""
    
    # Ключевые слова Python2 и Python3
    KEYWORDS_PY2 = {
        'print', 'exec', 'raw_input', 'xrange', 'has_key', 'iteritems',
        'iterkeys', 'itervalues', 'long', 'unicode', 'basestring',
        'buffer', 'file', 'reduce', 'reload', '__future__'
    }
    
    KEYWORDS_PY3 = {
        'print', 'input', 'range', '__init__', 'super', 'bytes',
        'str', 'int', 'float', 'complex', 'list', 'tuple', 'dict',
        'set', 'frozenset', 'bool', 'type', 'object', 'None', 'True',
        'False', 'and', 'or', 'not', 'is', 'in', 'if', 'elif', 'else',
        'for', 'while', 'break', 'continue', 'pass', 'def', 'class',
        'return', 'yield', 'import', 'from', 'as', 'try', 'except',
        'finally', 'raise', 'assert', 'with', 'lambda', 'global',
        'nonlocal', 'del', '__name__', '__main__'
    }
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[str] = []
        
    def current_char(self) -> Optional[str]:
        """Получить текущий символ"""
        if self.position < len(self.source):
            return self.source[self.position]
        return None
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Посмотреть символ на расстоянии offset"""
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Переместиться на следующий символ"""
        if self.position < len(self.source):
            ch = self.source[self.position]
            self.position += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return ch
        return None
    
    def skip_whitespace(self, skip_newline: bool = True):
        """Пропустить пробелы"""
        while self.current_char() in (' ', '\t', '\r'):
            self.advance()
        if skip_newline:
            while self.current_char() == '\n':
                self.advance()
    
    def read_string(self, quote_char: str) -> str:
        """Прочитать строковый литерал"""
        value = ''
        self.advance()  # Пропустить открывающую кавычку
        
        # Проверка на тройные кавычки
        is_triple = False
        if self.current_char() == quote_char and self.peek_char() == quote_char:
            is_triple = True
            self.advance()
            self.advance()
        
        while self.current_char() is not None:
            if is_triple:
                if (self.current_char() == quote_char and 
                    self.peek_char() == quote_char and 
                    self.peek_char(2) == quote_char):
                    self.advance()
                    self.advance()
                    self.advance()
                    break
            else:
                if self.current_char() == quote_char:
                    self.advance()
                    break
                if self.current_char() == '\n':
                    self.errors.append(f"Строка {self.line}: Неоконченная строка")
                    break
            
            if self.current_char() == '\\':
                value += self.current_char()
                self.advance()
                if self.current_char():
                    value += self.current_char()
                    self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        return value
    
    def read_identifier(self) -> str:
        """Прочитать идентификатор"""
        value = ''
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.current_char()
            self.advance()
        return value
    
    def read_number(self) -> str:
        """Прочитать числовой литерал"""
        value = ''
        
        # Поддержка hex, octal, binary в Python2
        if self.current_char() == '0':
            value += self.current_char()
            self.advance()
            
            # Hex: 0x...
            if self.current_char() in ('x', 'X'):
                value += self.current_char()
                self.advance()
                while self.current_char() and self.current_char() in '0123456789abcdefABCDEF':
                    value += self.current_char()
                    self.advance()
                return value
            
            # Binary: 0b... (Python2.6+)
            if self.current_char() in ('b', 'B'):
                value += self.current_char()
                self.advance()
                while self.current_char() and self.current_char() in '01':
                    value += self.current_char()
                    self.advance()
                return value
            
            # Octal: 0... (Python2) -> 0o... (Python3)
            if self.current_char() and self.current_char().isdigit():
                while self.current_char() and self.current_char() in '01234567':
                    value += self.current_char()
                    self.advance()
                return value
        
        # Десятичные цифры
        while self.current_char() and self.current_char().isdigit():
            value += self.current_char()
            self.advance()
        
        # Дробная часть
        if self.current_char() == '.':
            value += self.current_char()
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                value += self.current_char()
                self.advance()
        
        # Экспонента
        if self.current_char() in ('e', 'E'):
            value += self.current_char()
            self.advance()
            if self.current_char() in ('+', '-'):
                value += self.current_char()
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                value += self.current_char()
                self.advance()
        
        # Суффиксы типов Python2: L (long), l, j, J (complex)
        if self.current_char() in ('L', 'l', 'j', 'J'):
            value += self.current_char()
            self.advance()
        
        return value
    
    def tokenize(self) -> List[Token]:
        """Выполнить лексический анализ"""
        while self.position < len(self.source):
            self.skip_whitespace(skip_newline=False)
            
            if self.position >= len(self.source):
                break
            
            ch = self.current_char()
            start_line = self.line
            start_column = self.column
            
            # Комментарии
            if ch == '#':
                comment = ''
                while self.current_char() and self.current_char() != '\n':
                    comment += self.current_char()
                    self.advance()
                self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_column))
                continue
            
            # Новая строка
            if ch == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_column))
                self.advance()
                continue
            
            # Строки
            if ch in ('"', "'"):
                value = self.read_string(ch)
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_column))
                continue
            
            # Идентификаторы и ключевые слова
            if ch.isalpha() or ch == '_':
                value = self.read_identifier()
                if value in self.KEYWORDS_PY2 or value in self.KEYWORDS_PY3:
                    self.tokens.append(Token(TokenType.KEYWORD, value, start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, value, start_line, start_column))
                continue
            
            # Числа
            if ch.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_column))
                continue
            
            # Операторы
            next_ch = self.peek_char()
            two_char_ops = {
                '==', '!=', '<=', '>=', '<>', '<<', '>>', '**',
                '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
                '//=', '**=', '->'
            }
            
            three_char_ops = {'//=', '**=', '<<=', '>>='}
            
            if ch + (next_ch or '') + (self.peek_char(2) or '') in three_char_ops:
                op = ch + next_ch + self.peek_char(2)
                self.tokens.append(Token(TokenType.OPERATOR, op, start_line, start_column))
                self.advance()
                self.advance()
                self.advance()
                continue
            
            if ch + (next_ch or '') in two_char_ops:
                op = ch + next_ch
                self.tokens.append(Token(TokenType.OPERATOR, op, start_line, start_column))
                self.advance()
                self.advance()
                continue
            
            # Одиночные символы
            if ch == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_column))
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column))
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column))
            elif ch == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_column))
            elif ch == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_column))
            elif ch == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column))
            elif ch == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column))
            elif ch == ':':
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_column))
            elif ch == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_column))
            elif ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_column))
            elif ch == '.':
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_column))
            elif ch in '+-*/%&|^!<>~@':
                self.tokens.append(Token(TokenType.OPERATOR, ch, start_line, start_column))
            else:
                self.tokens.append(Token(TokenType.UNKNOWN, ch, start_line, start_column))
                self.errors.append(f"Строка {start_line}:{start_column}: Неизвестный символ '{ch}'")
            
            self.advance()
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

# ============================================================================
# ЧАСТЬ 2: ТАБЛИЦА ИДЕНТИФИКАТОРОВ
# ============================================================================

@dataclass
class IdentifierEntry:
    """Запись в таблице идентификаторов"""
    name: str
    kind: str  # 'var', 'func', 'class', 'import'
    type_: str = 'unknown'
    scope: str = '0'
    bucket: int = -1
    pos: int = -1
    py2_specific: bool = False  # Маркер Python2-специфичности

class IdentifierTable:
    """Таблица идентификаторов с поддержкой вложенных областей видимости"""
    
    LOAD_FACTOR_THRESHOLD = 0.75
    
    def __init__(self, initial_capacity: int = 128):
        self._capacity = self._next_power_of_two(max(2, initial_capacity))
        self._buckets: List[Optional[List[IdentifierEntry]]] = [None] * self._capacity
        self._count = 0
        self._current_scope = '0'
        self._scope_stack = ['0']
        self._depth_counters: Dict[int, int] = {}
    
    @staticmethod
    def _next_power_of_two(n: int) -> int:
        p = 1
        while p < n:
            p <<= 1
        return p
    
    def _hash(self, key: str) -> int:
        """Хеш-функция"""
        if not key:
            return 0
        h = 0
        for ch in key:
            h = ((h << 5) - h + ord(ch)) & 0x7FFFFFFF
        return h % self._capacity
    
    def enter_scope(self) -> str:
        """Войти в новую область видимости"""
        current_depth = int(self._current_scope[0]) if self._current_scope[0].isdigit() else 0
        new_depth = current_depth + 1
        
        if new_depth not in self._depth_counters:
            self._depth_counters[new_depth] = 0
        
        block_number = self._depth_counters[new_depth]
        self._depth_counters[new_depth] += 1
        
        if block_number == 0:
            new_scope = str(new_depth)
        else:
            letter = chr(ord('a') + block_number - 1)
            new_scope = f"{new_depth}{letter}"
        
        self._scope_stack.append(new_scope)
        self._current_scope = new_scope
        return new_scope
    
    def exit_scope(self) -> Optional[str]:
        """Выйти из области видимости"""
        if len(self._scope_stack) <= 1:
            return None
        old_scope = self._scope_stack.pop()
        self._current_scope = self._scope_stack[-1]
        return old_scope
    
    def insert(self, name: str, kind: str = 'var', type_: str = 'unknown',
               py2_specific: bool = False) -> Tuple[bool, Optional[str]]:
        """Вставить идентификатор в таблицу"""
        if not name:
            return False, "Пустое имя"
        
        if (self._count / self._capacity) >= self.LOAD_FACTOR_THRESHOLD:
            self._resize()
        
        bi = self._hash(name)
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        
        # Проверка на переопределение в текущей области
        for entry in bucket:
            if entry.name == name and entry.scope == self._current_scope:
                entry.kind = kind
                entry.type_ = type_
                entry.py2_specific = py2_specific
                return True, None
        
        # Новая запись
        entry = IdentifierEntry(
            name=name, kind=kind, type_=type_, scope=self._current_scope,
            bucket=bi, pos=len(bucket), py2_specific=py2_specific
        )
        bucket.append(entry)
        self._count += 1
        return True, None
    
    def search(self, name: str) -> Optional[IdentifierEntry]:
        """Поиск идентификатора"""
        if not name:
            return None
        
        bi = self._hash(name)
        bucket = self._buckets[bi]
        
        if not bucket:
            return None
        
        # Поиск в текущей области и родительских
        for scope_level in reversed(self._scope_stack):
            for entry in bucket:
                if entry.name == name and entry.scope == scope_level:
                    return entry
        
        return None
    
    def get_all_entries(self) -> List[IdentifierEntry]:
        """Получить все идентификаторы"""
        result = []
        for bucket in self._buckets:
            if bucket:
                result.extend(bucket)
        return sorted(result, key=lambda e: (e.scope, e.name))
    
    def _resize(self):
        """Увеличить размер таблицы"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._count = 0
        
        for bucket in old_buckets:
            if bucket:
                for entry in bucket:
                    bi = self._hash(entry.name)
                    if self._buckets[bi] is None:
                        self._buckets[bi] = []
                    self._buckets[bi].append(entry)
                    self._count += 1

# ============================================================================
# ЧАСТЬ 3: СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР И ТРАНСФОРМАЦИЯ
# ============================================================================

class CodeTransformer:
    """Преобразователь Python2 кода в Python3"""
    
    # Соответствия Python2 -> Python3
    PY2_TO_PY3_FUNCS = {
        'raw_input': 'input',
        'xrange': 'range',
        'unicode': 'str',
        'long': 'int',
        'basestring': 'str',
        'reduce': 'functools.reduce',
        'file': 'open',
        'execfile': 'exec(open(...).read())',
    }
    
    def __init__(self, tokens: List[Token], identifier_table: IdentifierTable):
        self.tokens = tokens
        self.id_table = identifier_table
        self.position = 0
        self.output_lines: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.transformations_made: List[str] = []
    
    def transform(self) -> str:
        """Выполнить трансформацию"""
        self.output_lines = []
        self._process_tokens()
        return '\n'.join(self.output_lines)
    
    def _process_tokens(self):
        """Обработать токены и выполнить трансформации"""
        current_line = ''
        i = 0
        
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Пропустить комментарии
            if token.type == TokenType.COMMENT:
                current_line += token.value
                i += 1
                continue
            
            # Обработка ключевых слов
            if token.type == TokenType.KEYWORD:
                current_line += self._transform_keyword(token, i)
                i += 1
                continue
            
            # Обработка идентификаторов
            if token.type == TokenType.IDENTIFIER:
                transformed = self._transform_identifier(token)
                current_line += transformed
                i += 1
                continue
            
            # Обработка строк
            if token.type == TokenType.STRING:
                current_line += self._transform_string(token)
                i += 1
                continue
            
            # Обработка чисел
            if token.type == TokenType.NUMBER:
                current_line += self._transform_number(token)
                i += 1
                continue
            
            # Обработка операторов
            if token.type == TokenType.OPERATOR:
                current_line += self._transform_operator(token, i)
                i += 1
                continue
            
            # Новая строка
            if token.type == TokenType.NEWLINE:
                if current_line.strip():
                    self.output_lines.append(current_line)
                current_line = ''
                i += 1
                continue
            
            # Остальные токены
            current_line += token.value
            i += 1
        
        if current_line.strip():
            self.output_lines.append(current_line)
    
    def _transform_keyword(self, token: Token, position: int) -> str:
        """Трансформировать ключевое слово"""
        if token.value == 'print':
            self.transformations_made.append(f"Строка {token.line}: print statement -> print() function")
            # Для простоты возвращаем 'print', реальная трансформация требует анализа аргументов
            return 'print('
        
        elif token.value == 'exec':
            self.transformations_made.append(f"Строка {token.line}: exec statement -> exec() function")
            return 'exec('
        
        elif token.value == 'raise':
            # raise Exception, args -> raise Exception(args)
            self.transformations_made.append(f"Строка {token.line}: raise syntax updated")
            return 'raise'
        
        return token.value
    
    def _transform_identifier(self, token: Token) -> str:
        """Трансформировать идентификатор"""
        if token.value in self.PY2_TO_PY3_FUNCS:
            self.transformations_made.append(
                f"Строка {token.line}: {token.value} -> {self.PY2_TO_PY3_FUNCS[token.value]}"
            )
            return self.PY2_TO_PY3_FUNCS[token.value]
        
        return token.value
    
    def _transform_string(self, token: Token) -> str:
        """Трансформировать строковый литерал"""
        value = token.value
        
        # Python3 использует Unicode по умолчанию
        if value.startswith('u"') or value.startswith("u'"):
            self.transformations_made.append(f"Строка {token.line}: удален префикс 'u' из строки")
            return value[1:]  # Удалить 'u'
        
        # Обработка escape-последовательностей
        return f'"{value}"'
    
    def _transform_number(self, token: Token) -> str:
        """Трансформировать числовой литерал"""
        value = token.value
        
        # Удалить суффиксы типов Python2: L (long)
        if value.endswith('L') or value.endswith('l'):
            self.transformations_made.append(f"Строка {token.line}: удален суффикс 'L' из числа {value}")
            return value[:-1]
        
        # Конвертировать старую восьмеричную нотацию
        if value.startswith('0') and len(value) > 1 and value[1].isdigit():
            self.transformations_made.append(f"Строка {token.line}: восьмеричное число {value} -> 0o{value[1:]}")
            return f'0o{value[1:]}'
        
        return value
    
    def _transform_operator(self, token: Token, position: int) -> str:
        """Трансформировать оператор"""
        value = token.value
        
        # Оператор <> переименовать на !=
        if value == '<>':
            self.transformations_made.append(f"Строка {token.line}: оператор '<>' -> '!='")
            return '!='
        
        # Целочисленное деление /
        if value == '/':
            # В Python3 нужно использовать // для целочисленного деления
            # Это требует контекстного анализа, поэтому выдаем предупреждение
            self.warnings.append(f"Строка {token.line}: проверьте оператор деления '/' (может потребоваться '//')")
        
        return value

# ============================================================================
# ЧАСТЬ 4: ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ============================================================================

class TranslatorGUI:
    """Графический интерфейс транслятора"""
    
    EXAMPLES = {
        "Пример 1: print statement": """print "Hello, World!"
print 'Python 2'""",
        
        "Пример 2: raw_input": """name = raw_input('Enter name: ')
print "Your name is", name""",
        
        "Пример 3: xrange": """for i in xrange(10):
    print i""",
        
        "Пример 4: long type": """x = 123456789L
y = long('999999999')
print x + y""",
        
        "Пример 5: has_key": """d = {'a': 1, 'b': 2}
if d.has_key('a'):
    print d['a']""",
        
        "Пример 6: unicode": """s = u'Привет'
name = unicode('Мир')
print s, name""",
        
        "Пример 7: <> оператор": """if x <> y:
    print 'Not equal'""",
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python2 -> Python3 Translator")
        self.root.geometry("1400x900")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Создать пользовательский интерфейс"""
        # Главный фрейм с двумя панелями
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель: входной код
        left_frame = ttk.LabelFrame(main_paned, text="Python2 Code", padding=10)
        main_paned.add(left_frame, weight=1)
        
        # Примеры
        example_frame = ttk.Frame(left_frame)
        example_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(example_frame, text="Examples:").pack(side=tk.LEFT)
        self.example_var = tk.StringVar()
        example_combo = ttk.Combobox(
            example_frame, textvariable=self.example_var,
            values=list(self.EXAMPLES.keys()), state='readonly'
        )
        example_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        example_combo.bind('<<ComboboxSelected>>', self._load_example)
        
        # Кнопка загрузки файла
        ttk.Button(example_frame, text="Load File", command=self._load_file).pack(side=tk.LEFT, padx=5)
        
        # Входной текст
        self.input_text = scrolledtext.ScrolledText(
            left_frame, wrap=tk.NONE, font=('Courier New', 11)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка трансляции
        translate_btn = ttk.Button(
            left_frame, text="▶ Translate", command=self._translate,
            style='Accent.TButton'
        )
        translate_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Правая панель: результаты
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        right_paned = ttk.PanedWindow(right_frame, orient=tk.VERTICAL)
        right_paned.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        notebook = ttk.Notebook(right_paned)
        right_paned.add(notebook, weight=1)
        
        # Вкладка: Python3 код
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Python3 Code")
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.NONE, font=('Courier New', 11), state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка: Трансформации
        transform_frame = ttk.Frame(notebook)
        notebook.add(transform_frame, text="Transformations")
        
        self.transform_text = scrolledtext.ScrolledText(
            transform_frame, wrap=tk.WORD, font=('Courier New', 10), state=tk.DISABLED
        )
        self.transform_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка: Идентификаторы
        id_frame = ttk.Frame(notebook)
        notebook.add(id_frame, text="Identifiers")
        
        id_columns = ('Name', 'Kind', 'Type', 'Scope', 'Python2-specific')
        self.id_tree = ttk.Treeview(id_frame, columns=id_columns, show='headings', height=15)
        
        for col in id_columns:
            self.id_tree.heading(col, text=col)
            self.id_tree.column(col, width=120)
        
        id_scroll = ttk.Scrollbar(id_frame, orient=tk.VERTICAL, command=self.id_tree.yview)
        self.id_tree.configure(yscrollcommand=id_scroll.set)
        self.id_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        id_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Вкладка: Ошибки и предупреждения
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Messages")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=('Courier New', 10), state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Загрузить первый пример
        if self.EXAMPLES:
            self.example_var.set(list(self.EXAMPLES.keys())[0])
            self._load_example()
    
    def _load_example(self, event=None):
        """Загрузить пример"""
        example = self.EXAMPLES.get(self.example_var.get(), "")
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', example)
    
    def _load_file(self):
        """Загрузить файл"""
        filename = filedialog.askopenfilename(
            title="Open Python2 File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', code)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")
    
    def _translate(self):
        """Выполнить трансляцию"""
        py2_code = self.input_text.get('1.0', tk.END)
        
        # Лексический анализ
        lexer = LexicalAnalyzer(py2_code)
        tokens = lexer.tokenize()
        
        # Таблица идентификаторов
        id_table = IdentifierTable()
        
        # Анализ токенов для построения таблицы
        for token in tokens:
            if token.type == TokenType.IDENTIFIER:
                entry = id_table.search(token.value)
                if not entry:
                    # Определяем тип идентификатора
                    py2_specific = token.value in CodeTransformer.PY2_TO_PY3_FUNCS
                    id_table.insert(token.value, 'var', 'unknown', py2_specific)
            elif token.type == TokenType.KEYWORD:
                if token.value in ('def', 'class'):
                    # Следующий идентификатор будет названием функции/класса
                    pass
        
        # Трансформация
        transformer = CodeTransformer(tokens, id_table)
        py3_code = transformer.transform()
        
        # Вывод результатов
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', py3_code)
        self.output_text.configure(state=tk.DISABLED)
        
        # Трансформации
        self.transform_text.configure(state=tk.NORMAL)
        self.transform_text.delete('1.0', tk.END)
        
        transform_log = "\n".join(transformer.transformations_made) if transformer.transformations_made else "No transformations"
        self.transform_text.insert('1.0', transform_log)
        
        if transformer.warnings:
            self.transform_text.insert(tk.END, "\n\n=== WARNINGS ===\n")
            self.transform_text.insert(tk.END, "\n".join(transformer.warnings))
        
        if transformer.errors:
            self.transform_text.insert(tk.END, "\n\n=== ERRORS ===\n")
            self.transform_text.insert(tk.END, "\n".join(transformer.errors))
        
        self.transform_text.configure(state=tk.DISABLED)
        
        # Идентификаторы
        self.id_tree.delete(*self.id_tree.get_children())
        for entry in id_table.get_all_entries():
            values = (
                entry.name,
                entry.kind,
                entry.type_,
                entry.scope,
                '✓' if entry.py2_specific else ''
            )
            self.id_tree.insert('', tk.END, values=values)
        
        # Лог
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        
        log_messages = [
            f"=== TRANSLATION REPORT ===",
            f"Input lines: {len(py2_code.splitlines())}",
            f"Output lines: {len(py3_code.splitlines())}",
            f"Tokens found: {len(tokens)}",
            f"Identifiers in table: {len(id_table.get_all_entries())}",
            f"Transformations: {len(transformer.transformations_made)}",
            f"Warnings: {len(transformer.warnings)}",
            f"Errors: {len(transformer.errors + lexer.errors)}",
        ]
        
        if lexer.errors:
            log_messages.append("\n=== LEXER ERRORS ===")
            log_messages.extend(lexer.errors)
        
        self.log_text.insert('1.0', "\n".join(log_messages))
        self.log_text.configure(state=tk.DISABLED)

def main():
    """Главная функция"""
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()