#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Определение типов токенов для Python лексера
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    """Типы токенов Python"""
    # Ключевые слова Python 2/3
    AND = auto()
    AS = auto()
    ASSERT = auto()
    BREAK = auto()
    CLASS = auto()
    CONTINUE = auto()
    DEF = auto()
    DEL = auto()
    ELIF = auto()
    ELSE = auto()
    EXCEPT = auto()
    EXEC = auto()  # Python 2
    FINALLY = auto()
    FOR = auto()
    FROM = auto()
    GLOBAL = auto()
    IF = auto()
    IMPORT = auto()
    IN = auto()
    IS = auto()
    LAMBDA = auto()
    NOT = auto()
    OR = auto()
    PASS = auto()
    PRINT = auto()  # Python 2
    RAISE = auto()
    RETURN = auto()
    TRY = auto()
    WHILE = auto()
    WITH = auto()
    YIELD = auto()
    NONE = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Операторы
    PLUS = auto()          # +
    MINUS = auto()         # -
    MULTIPLY = auto()      # *
    DIVIDE = auto()        # /
    FLOOR_DIVIDE = auto()  # //
    MODULO = auto()        # %
    POWER = auto()         # **
    
    # Операторы сравнения
    EQ = auto()            # ==
    NE = auto()            # !=
    LT = auto()            # <
    LE = auto()            # <=
    GT = auto()            # >
    GE = auto()            # >=
    
    # Присваивание
    ASSIGN = auto()        # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    MULT_ASSIGN = auto()   # *=
    DIV_ASSIGN = auto()    # /=
    MOD_ASSIGN = auto()    # %=
    
    # Разделители
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    COMMA = auto()         # ,
    COLON = auto()         # :
    SEMICOLON = auto()     # ;
    DOT = auto()           # .
    ARROW = auto()         # ->
    
    # Литералы
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Специальные
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Токен с метаданными"""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


# Ключевые слова Python 2 и Python 3
PYTHON2_KEYWORDS = {
    'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
    'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
    'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
    'raise', 'return', 'try', 'while', 'with', 'yield', 'None', 'True', 'False'
}

PYTHON3_KEYWORDS = {
    'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
    'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
    'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass',
    'raise', 'return', 'try', 'while', 'with', 'yield', 'None', 'True', 'False',
    'nonlocal', 'async', 'await'
}

# Маппинг ключевых слов к типам токенов
KEYWORD_MAP = {
    'and': TokenType.AND,
    'as': TokenType.AS,
    'assert': TokenType.ASSERT,
    'break': TokenType.BREAK,
    'class': TokenType.CLASS,
    'continue': TokenType.CONTINUE,
    'def': TokenType.DEF,
    'del': TokenType.DEL,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'except': TokenType.EXCEPT,
    'exec': TokenType.EXEC,
    'finally': TokenType.FINALLY,
    'for': TokenType.FOR,
    'from': TokenType.FROM,
    'global': TokenType.GLOBAL,
    'if': TokenType.IF,
    'import': TokenType.IMPORT,
    'in': TokenType.IN,
    'is': TokenType.IS,
    'lambda': TokenType.LAMBDA,
    'not': TokenType.NOT,
    'or': TokenType.OR,
    'pass': TokenType.PASS,
    'print': TokenType.PRINT,
    'raise': TokenType.RAISE,
    'return': TokenType.RETURN,
    'try': TokenType.TRY,
    'while': TokenType.WHILE,
    'with': TokenType.WITH,
    'yield': TokenType.YIELD,
    'None': TokenType.NONE,
    'True': TokenType.TRUE,
    'False': TokenType.FALSE
}
