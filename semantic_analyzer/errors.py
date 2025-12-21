#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Описание семантических ошибок
"""

from enum import Enum, auto


class ErrorType(Enum):
    """Типы семантических ошибок"""
    
    # Функции
    ARGUMENT_COUNT_MISMATCH = auto()      # Несовпадение количества аргументов
    DUPLICATE_ARGUMENT = auto()            # Дублирование имен аргументов
    RETURN_OUTSIDE_FUNCTION = auto()       # Return вне функции
    YIELD_OUTSIDE_FUNCTION = auto()        # Yield вне функции
    
    # Циклы
    BREAK_OUTSIDE_LOOP = auto()            # Break вне цикла
    CONTINUE_OUTSIDE_LOOP = auto()         # Continue вне цикла
    
    # Переменные
    UNDECLARED_IDENTIFIER = auto()         # Использование необъявленной переменной
    REDEFINITION_BUILTIN = auto()          # Переопределение встроенной функции
    
    # Константы
    CONST_DIVISION_BY_ZERO = auto()        # Деление на ноль (константа)
    
    # Мертвый код
    DEAD_CODE = auto()                     # Недостижимый код


class SemanticError:
    """Представление семантической ошибки"""
    
    def __init__(self, error_type: ErrorType, message: str, line: int, column: int):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column
    
    def __str__(self) -> str:
        return f"Строка {self.line}:{self.column}: [{self.error_type.name}] {self.message}"
    
    def __repr__(self) -> str:
        return f"SemanticError({self.error_type.name}, {repr(self.message)}, {self.line}, {self.column})"


class SemanticWarning:
    """Представление семантического предупреждения"""
    
    def __init__(self, error_type: ErrorType, message: str, line: int, column: int):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column
    
    def __str__(self) -> str:
        return f"Строка {self.line}:{self.column}: [WARNING: {self.error_type.name}] {self.message}"
    
    def __repr__(self) -> str:
        return f"SemanticWarning({self.error_type.name}, {repr(self.message)}, {self.line}, {self.column})"
