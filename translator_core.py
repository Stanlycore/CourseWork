#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Транслятор Python 2 → Python 3
Основной модуль с полной поддержкой всех различий между версиями
Вариант 12: Вложенные структуры, таблица идентификаторов через цепочки
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import re
from abc import ABC, abstractmethod


# ============================================================
# РАЗЛИЧИЯ PYTHON 2 VS PYTHON 3
# ============================================================

PYTHON2_TO_PYTHON3_CHANGES = {
    # PRINT: statement → function
    'print_statement': {
        'pattern': r'print\s+(.+)',
        'replacement': lambda match: f'print({match.group(1)})',
        'description': 'print statement -> print() function'
    },
    
    # UNICODE: all strings are unicode by default
    'unicode_literals': {
        'description': 'All strings are unicode by default in Python 3',
        'python2_syntax': 'u"string" or "string" (ASCII)',
        'python3_syntax': '"string" (unicode)'
    },
    
    # INTEGER DIVISION: / now returns float
    'integer_division': {
        'pattern': r'(\d+)\s*/\s*(\d+)',
        'python2_result': 'floor division (integer)',
        'python3_result': 'true division (float)',
        'use_floor_division': '//',
        'description': 'Use // for floor division in Python 3'
    },
    
    # XRANGE → RANGE
    'xrange_to_range': {
        'pattern': r'\bxrange\b',
        'replacement': 'range',
        'description': 'xrange() removed, range() is now lazy'
    },
    
    # EXCEPTION HANDLING: except X, e → except X as e
    'exception_syntax': {
        'pattern': r'except\s+(\w+)\s*,\s*(\w+)',
        'replacement': lambda m: f'except {m.group(1)} as {m.group(2)}',
        'description': 'except clause syntax changed'
    },
    
    # ITERATORS: dict.keys(), dict.values(), dict.items() return views
    'dict_methods': {
        'keys': 'returns view (iterable), not list',
        'values': 'returns view (iterable), not list',
        'items': 'returns view (iterable), not list',
        'note': 'wrap with list() if you need a list'
    },
    
    # COMPARISON: no more <> operator
    'comparison_operators': {
        'pattern': r'(<>)',
        'replacement': '!=',
        'description': '<> operator removed, use !='
    },
    
    # IMPORTS: relative imports must be explicit
    'import_changes': {
        'description': 'Relative imports must use . or ..'
    },
    
    # RAW_INPUT → INPUT
    'raw_input': {
        'pattern': r'\braw_input\b',
        'replacement': 'input',
        'description': 'raw_input() removed, input() now returns string'
    },
    
    # BASESTRING removed
    'basestring': {
        'pattern': r'\bbasestring\b',
        'replacement': 'str',
        'description': 'basestring removed, use str instead'
    },
    
    # UNICODE TYPE removed
    'unicode_type': {
        'pattern': r'\bunicode\b',
        'replacement': 'str',
        'description': 'unicode type removed, str is now unicode'
    },
    
    # LONG TYPE removed
    'long_type': {
        'pattern': r'(\d+)L\b',
        'replacement': lambda m: m.group(1),
        'description': 'long type removed, int is now unlimited'
    },
    
    # ITERATORS: map, filter, zip return iterators, not lists
    'map_filter_zip': {
        'map': 'returns iterator, not list',
        'filter': 'returns iterator, not list',
        'zip': 'returns iterator, not list'
    },
    
    # EXEC: statement → function
    'exec_statement': {
        'pattern': r'exec\s+(.+)',
        'replacement': lambda m: f'exec({m.group(1)})',
        'description': 'exec statement -> exec() function'
    },
    
    # REDUCE moved to functools
    'reduce_function': {
        'pattern': r'\breduce\b',
        'replacement': 'functools.reduce',
        'import': 'from functools import reduce',
        'description': 'reduce() moved to functools module'
    },
}


# ============================================================
# ТИПЫ ТОКЕНОВ
# ============================================================

class TokenType(Enum):
    """Типы лексем"""
    # Литералы
    NUMBER = auto()
    STRING = auto()
    BYTES = auto()
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    
    # Идентификаторы и ключевые слова
    IDENTIFIER = auto()
    KEYWORD = auto()
    BUILTIN = auto()
    
    # Операторы
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    FLOOR_SLASH = auto()
    PERCENT = auto()
    POWER = auto()
    
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()
    
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    NOT_IN = auto()
    IS = auto()
    IS_NOT = auto()
    
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    BITWISE_NOT = auto()
    LSHIFT = auto()
    RSHIFT = auto()
    
    # Пунктуация
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()
    ELLIPSIS = auto()
    ARROW = auto()
    
    # Управление потоком
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    
    # Специальные
    EOF = auto()
    UNKNOWN = auto()
    ERROR = auto()


@dataclass
class Token:
    """Токен - результат лексического анализа"""
    type: TokenType
    value: Any
    line: int
    column: int
    original: str = ""
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}, {self.column})"


# ============================================================
# ТАБЛИЦА ИДЕНТИФИКАТОРОВ С ПОДДЕРЖКОЙ SCOPE
# ============================================================

@dataclass
class IdentifierEntry:
    """Запись в таблице идентификаторов"""
    name: str
    kind: str = "variable"  # variable, function, class, import
    type_: str = "Any"
    value: Optional[Any] = None
    scope: str = "0"  # глобальная область
    line: int = 0
    column: int = 0
    bucket: int = -1
    pos: int = -1
    
    def __repr__(self):
        return f"ID({self.name}, {self.kind}, scope={self.scope}, addr=({self.bucket},{self.pos}))"


class ScopedIdentifierTable:
    """Таблица идентификаторов с поддержкой вложенных областей видимости"""
    
    LOAD_FACTOR_THRESHOLD = 0.75
    
    def __init__(self, initial_capacity: int = 128):
        self._capacity = self._next_power_of_two(max(2, initial_capacity))
        self._buckets: List[Optional[List[IdentifierEntry]]] = [None] * self._capacity
        self._count = 0
        self._current_scope = "0"
        self._scope_stack = ["0"]
        self._depth_block_counters: Dict[int, int] = {}
        self._total_probes = 0
        self._insertions = 0
        self._searches = 0
        self._collisions = 0
    
    def _next_power_of_two(self, n: int) -> int:
        """Найти следующую степень двойки"""
        p = 1
        while p < n:
            p <<= 1
        return p
    
    def _hash(self, key: str) -> int:
        """Хеш-функция Сила"""
        if not key:
            return 0
        h = 0
        for ch in key:
            h = ((h << 5) - h + ord(ch)) & 0x7FFFFFFF
        return h % self._capacity
    
    def _is_valid_identifier(self, name: str) -> bool:
        """Проверить валидность идентификатора"""
        if not name or not isinstance(name, str):
            return False
        if name[0].isdigit():
            return False
        return all(c.isalnum() or c == '_' for c in name)
    
    def _get_scope_depth(self, scope: str) -> int:
        """Получить глубину scope"""
        if scope == "0":
            return 0
        depth_str = ""
        for ch in scope:
            if ch.isdigit():
                depth_str += ch
            else:
                break
        return int(depth_str) if depth_str else 0
    
    def enter_scope(self) -> str:
        """Войти в новую область видимости"""
        current_depth = self._get_scope_depth(self._current_scope)
        new_depth = current_depth + 1
        
        if new_depth not in self._depth_block_counters:
            self._depth_block_counters[new_depth] = 0
        
        block_number = self._depth_block_counters[new_depth]
        self._depth_block_counters[new_depth] += 1
        
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
    
    def get_current_scope(self) -> str:
        """Получить текущую область видимости"""
        return self._current_scope
    
    def _resize(self) -> None:
        """Перестроить таблицу при переполнении"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._count = 0
        
        for bucket in old_buckets:
            if bucket:
                for entry in bucket:
                    self._insert_entry(entry)
    
    def _insert_entry(self, entry: IdentifierEntry) -> bool:
        """Вставить запись в таблицу (внутреннее)"""
        bi = self._hash(entry.name)
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        entry.bucket, entry.pos = bi, len(bucket)
        bucket.append(entry)
        self._count += 1
        return True
    
    def insert(self, name: str, kind: str = "variable", type_: str = "Any",
               value: Optional[Any] = None, line: int = 0, column: int = 0) -> Tuple[bool, Optional[str]]:
        """Вставить идентификатор"""
        if not name:
            return False, "Пустое имя идентификатора"
        
        if not self._is_valid_identifier(name):
            return False, f"Недопустимое имя: {name}"
        
        if (self._count / self._capacity) >= self.LOAD_FACTOR_THRESHOLD:
            self._resize()
        
        bi = self._hash(name)
        self._total_probes += 1
        
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        
        # Проверка на дубликат в текущей scope
        for i, existing in enumerate(bucket):
            self._total_probes += 1
            if existing.name == name and existing.scope == self._current_scope:
                existing.kind = kind
                existing.type_ = type_
                existing.value = value
                existing.line = line
                existing.column = column
                return True, None
        
        entry = IdentifierEntry(
            name=name, kind=kind, type_=type_, value=value,
            scope=self._current_scope, line=line, column=column,
            bucket=bi, pos=len(bucket)
        )
        bucket.append(entry)
        self._count += 1
        self._insertions += 1
        
        if len(bucket) > 1:
            self._collisions += 1
        
        return True, None
    
    def search(self, name: str) -> Optional[IdentifierEntry]:
        """Поиск идентификатора с учетом scope"""
        if not name:
            return None
        
        bi = self._hash(name)
        self._total_probes += 1
        self._searches += 1
        
        bucket = self._buckets[bi]
        if not bucket:
            return None
        
        # Ищем с учетом иерархии scope
        for scope_level in reversed(self._scope_stack):
            for entry in bucket:
                self._total_probes += 1
                if entry.name == name and entry.scope == scope_level:
                    return entry
        
        return None
    
    def get_all_entries(self) -> List[IdentifierEntry]:
        """Получить все записи"""
        result = []
        for bucket in self._buckets:
            if bucket:
                result.extend(bucket)
        
        def scope_sort_key(entry: IdentifierEntry) -> Tuple:
            scope = entry.scope
            if scope == "0":
                return (0, "")
            depth = self._get_scope_depth(scope)
            letter = scope[len(str(depth)):] if len(scope) > len(str(depth)) else ""
            return (depth, letter)
        
        return sorted(result, key=lambda e: (scope_sort_key(e), e.name))
    
    def get_all_scopes(self) -> List[str]:
        """Получить все области видимости"""
        scopes = set()
        for bucket in self._buckets:
            if bucket:
                for entry in bucket:
                    scopes.add(entry.scope)
        
        return sorted(scopes, key=lambda s: (self._get_scope_depth(s), s))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику таблицы"""
        return {
            'capacity': self._capacity,
            'count': self._count,
            'load_factor': self._count / self._capacity if self._capacity > 0 else 0,
            'insertions': self._insertions,
            'searches': self._searches,
            'collisions': self._collisions,
            'total_probes': self._total_probes,
            'current_scope': self._current_scope,
            'scope_stack': self._scope_stack,
            'scopes': self.get_all_scopes(),
        }


print("translator_core.py loaded successfully")
