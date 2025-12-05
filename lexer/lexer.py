#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лексический анализатор для Python 2/3
"""

from typing import List, Optional
from .tokens import Token, TokenType, KEYWORD_MAP, PYTHON2_KEYWORDS
from identifier_table import IdentifierTable


class Lexer:
    """Лексический анализатор с поддержкой отступов"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[str] = []
        
        # Таблица идентификаторов
        self.identifier_table = IdentifierTable()
        
        # Стек отступов для INDENT/DEDENT
        self.indent_stack = [0]
        self.at_line_start = True
        
    def current_char(self) -> Optional[str]:
        """Текущий символ"""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Смотреть вперёд"""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Продвинуться на символ вперёд"""
        if self.pos < len(self.source):
            ch = self.source[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
                self.at_line_start = True
            else:
                self.column += 1
            return ch
        return None
    
    def skip_whitespace(self, skip_newline: bool = False):
        """Пропустить пробелы (но не новые строки, если не указано)"""
        while self.current_char():
            ch = self.current_char()
            if ch == ' ' or ch == '\t':
                self.advance()
            elif ch == '\n' and skip_newline:
                self.advance()
            else:
                break
    
    def handle_indentation(self):
        """Обработка отступов в начале строки"""
        if not self.at_line_start:
            return
        
        indent_level = 0
        start_line = self.line
        start_col = self.column
        
        # Считаем пробелы и табы
        while self.current_char() in (' ', '\t'):
            if self.current_char() == ' ':
                indent_level += 1
            else:  # tab
                indent_level += 4
            self.advance()
        
        # Пропустить пустые строки и комментарии
        if self.current_char() in ('\n', '#', None):
            return
        
        self.at_line_start = False
        
        # Сравниваем с текущим уровнем отступа
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, indent_level, start_line, start_col))
            # Входим в новую область видимости
            self.identifier_table.enter_scope()
        elif indent_level < current_indent:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, indent_level, start_line, start_col))
                # Выходим из области видимости
                self.identifier_table.exit_scope()
            
            if self.indent_stack[-1] != indent_level:
                self.errors.append(
                    f"Строка {start_line}:{start_col}: Некорректный уровень отступа"
                )
    
    def read_identifier_or_keyword(self) -> Token:
        """Чтение идентификатора или ключевого слова"""
        start_line = self.line
        start_column = self.column
        value = ''
        
        # Первый символ: буква или _
        if self.current_char() and (self.current_char().isalpha() or self.current_char() == '_'):
            value += self.advance()
        
        # Остальные: буквы, цифры, _
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.advance()
        
        # Проверка на ключевое слово
        if value in KEYWORD_MAP:
            return Token(KEYWORD_MAP[value], value, start_line, start_column)
        
        # Добавляем идентификатор в таблицу
        success, error = self.identifier_table.insert(value, kind="var", type_="auto")
        if not success:
            self.errors.append(f"Строка {start_line}:{start_column}: {error}")
        
        return Token(TokenType.IDENTIFIER, value, start_line, start_column)
    
    def read_number(self) -> Token:
        """Чтение числа (int, float, hex, octal, binary)"""
        start_line = self.line
        start_column = self.column
        value = ''
        
        # Hex: 0x...
        if self.current_char() == '0' and self.peek_char() in ('x', 'X'):
            value += self.advance()  # 0
            value += self.advance()  # x
            while self.current_char() and self.current_char() in '0123456789abcdefABCDEF':
                value += self.advance()
            try:
                return Token(TokenType.NUMBER, int(value, 16), start_line, start_column)
            except ValueError:
                self.errors.append(f"Строка {start_line}:{start_column}: Некорректное hex число '{value}'")
                return Token(TokenType.UNKNOWN, value, start_line, start_column)
        
        # Binary: 0b...
        if self.current_char() == '0' and self.peek_char() in ('b', 'B'):
            value += self.advance()  # 0
            value += self.advance()  # b
            while self.current_char() and self.current_char() in '01':
                value += self.advance()
            try:
                return Token(TokenType.NUMBER, int(value, 2), start_line, start_column)
            except ValueError:
                self.errors.append(f"Строка {start_line}:{start_column}: Некорректное binary число '{value}'")
                return Token(TokenType.UNKNOWN, value, start_line, start_column)
        
        # Octal: 0o... (Python3) или 0... (Python2)
        if self.current_char() == '0' and self.peek_char() in ('o', 'O'):
            value += self.advance()  # 0
            value += self.advance()  # o
            while self.current_char() and self.current_char() in '01234567':
                value += self.advance()
            try:
                return Token(TokenType.NUMBER, int(value, 8), start_line, start_column)
            except ValueError:
                self.errors.append(f"Строка {start_line}:{start_column}: Некорректное octal число '{value}'")
                return Token(TokenType.UNKNOWN, value, start_line, start_column)
        
        # Обычное число
        is_float = False
        while self.current_char() and self.current_char().isdigit():
            value += self.advance()
        
        # Дробная часть
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            is_float = True
            value += self.advance()  # .
            while self.current_char() and self.current_char().isdigit():
                value += self.advance()
        
        # Экспонента
        if self.current_char() in ('e', 'E'):
            is_float = True
            value += self.advance()
            if self.current_char() in ('+', '-'):
                value += self.advance()
            while self.current_char() and self.current_char().isdigit():
                value += self.advance()
        
        try:
            num_value = float(value) if is_float else int(value)
            return Token(TokenType.NUMBER, num_value, start_line, start_column)
        except ValueError:
            self.errors.append(f"Строка {start_line}:{start_column}: Некорректное число '{value}'")
            return Token(TokenType.UNKNOWN, value, start_line, start_column)
    
    def read_string(self, quote: str) -> Token:
        """Чтение строки (одинарные или двойные кавычки, тройные)"""
        start_line = self.line
        start_column = self.column
        value = ''
        
        # Проверка на тройные кавычки
        is_triple = (self.peek_char() == quote and 
                    self.peek_char(2) == quote)
        
        if is_triple:
            self.advance()  # первая
            self.advance()  # вторая
            self.advance()  # третья
            
            # Читаем до закрывающих тройных кавычек
            while self.current_char():
                if (self.current_char() == quote and 
                    self.peek_char() == quote and 
                    self.peek_char(2) == quote):
                    self.advance()
                    self.advance()
                    self.advance()
                    break
                value += self.advance()
        else:
            self.advance()  # открывающая кавычка
            
            # Читаем до закрывающей кавычки
            while self.current_char() and self.current_char() != quote:
                if self.current_char() == '\\':
                    self.advance()
                    escape_char = self.advance()
                    if escape_char:
                        # Обработка escape-последовательностей
                        escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', quote: quote}
                        value += escape_map.get(escape_char, escape_char)
                else:
                    value += self.advance()
            
            if self.current_char() == quote:
                self.advance()  # закрывающая кавычка
            else:
                self.errors.append(
                    f"Строка {start_line}:{start_column}: Незакрытая строка"
                )
        
        return Token(TokenType.STRING, value, start_line, start_column)
    
    def scan(self) -> List[Token]:
        """Главный цикл сканирования"""
        while self.pos < len(self.source):
            # Обработка отступов в начале строки
            self.handle_indentation()
            
            ch = self.current_char()
            if not ch:
                break
            
            start_line = self.line
            start_col = self.column
            
            # Пробелы
            if ch in (' ', '\t'):
                self.skip_whitespace()
                continue
            
            # Новая строка
            if ch == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_col))
                self.advance()
                continue
            
            # Комментарии
            if ch == '#':
                while self.current_char() and self.current_char() != '\n':
                    self.advance()
                continue
            
            # Идентификаторы и ключевые слова
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier_or_keyword())
                continue
            
            # Числа
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Строки
            if ch in ('"', "'"):
                self.tokens.append(self.read_string(ch))
                continue
            
            # Операторы и разделители
            self.advance()
            
            # Двухсимвольные операторы
            if ch == '=' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
            elif ch == '!' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.NE, '!=', start_line, start_col))
            elif ch == '<' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
            elif ch == '>' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
            elif ch == '+' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_col))
            elif ch == '-' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_col))
            elif ch == '*' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.MULT_ASSIGN, '*=', start_line, start_col))
            elif ch == '/' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.DIV_ASSIGN, '/=', start_line, start_col))
            elif ch == '%' and self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.MOD_ASSIGN, '%=', start_line, start_col))
            elif ch == '*' and self.current_char() == '*':
                self.advance()
                self.tokens.append(Token(TokenType.POWER, '**', start_line, start_col))
            elif ch == '/' and self.current_char() == '/':
                self.advance()
                self.tokens.append(Token(TokenType.FLOOR_DIVIDE, '//', start_line, start_col))
            elif ch == '-' and self.current_char() == '>':
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
            # Односимвольные
            elif ch == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            elif ch == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            elif ch == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
            elif ch == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
            elif ch == '%':
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
            elif ch == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            elif ch == '<':
                self.tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            elif ch == '>':
                self.tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            elif ch == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            elif ch == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            elif ch == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
            elif ch == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
            elif ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            elif ch == ':':
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
            elif ch == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_col))
            elif ch == '.':
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
            else:
                self.errors.append(
                    f"Строка {start_line}:{start_col}: Неизвестный символ '{ch}'"
                )
                self.tokens.append(Token(TokenType.UNKNOWN, ch, start_line, start_col))
        
        # Добавляем DEDENT для всех оставшихся уровней отступа
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, 0, self.line, self.column))
            self.identifier_table.exit_scope()
        
        # Финальный EOF
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        return self.tokens
