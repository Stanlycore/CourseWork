#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синтаксический анализатор Python с поддержкой вложенных структур
Вариант 12: полная поддержка scope, корректная обработка INDENT/DEDENT
ФАЗА 1 ИСПРАВЛЕНИЯ: null-checking и защита рекурсии
"""

from typing import List, Optional
from lexer import Token, TokenType
from .ast_nodes import *


class Pass(ASTNode):
    """Оператор pass"""
    pass


class Break(ASTNode):
    """Оператор break"""
    pass


class Continue(ASTNode):
    """Оператор continue"""
    pass


class Parser:
    """Синтаксический анализатор Python с защитой от infinite loops и правильным scope management"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[str] = []
        self._recursion_depth = 0
        self._max_recursion_depth = 100  # Защита от бесконечной рекурсии
    
    def current_token(self) -> Token:
        """Текущий токен"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek_token(self, offset: int = 1) -> Token:
        """Смотреть вперёд"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        """Перейти к следующему токену"""
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Optional[Token]:
        """Ожидать конкретный тип токена"""
        token = self.current_token()
        if token.type == token_type:
            return self.advance()
        
        self.errors.append(
            f"Строка {token.line}:{token.column}: "
            f"Ожидался {token_type.name}, но получен {token.type.name} ({token.value})"
        )
        return None
    
    def skip_newlines(self):
        """Пропустить пустые строки"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """Главная функция парсинга"""
        program = Program()
        
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            
            if self.current_token().type == TokenType.EOF:
                break
            
            # Сохраняем позицию для защиты от зацикливания
            old_pos = self.pos
            
            stmt = self._parse_statement()
            if stmt is not None:  # Явная проверка на None
                program.body.append(stmt)
            
            # КРИТИЧЕСКИ ВАЖНО: если позиция не изменилась, принудительно продвигаемся
            if self.pos == old_pos:
                token = self.current_token()
                self.errors.append(
                    f"Строка {token.line}:{token.column}: "
                    f"Не удалось разобрать инструкцию. Пропуск токена {token.type.name}."
                )
                self.advance()
        
        return program
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Разбор одной инструкции (внутренняя функция с защитой рекурсии)"""
        # Защита от бесконечной рекурсии
        if self._recursion_depth >= self._max_recursion_depth:
            token = self.current_token()
            self.errors.append(
                f"Строка {token.line}:{token.column}: Слишком глубокая вложенность (>{self._max_recursion_depth})"
            )
            # Вернуть None, но не зацикливаться
            self.advance()
            return None
        
        self._recursion_depth += 1
        try:
            result = self._parse_statement_impl()
        finally:
            self._recursion_depth -= 1
        
        return result
    
    def _parse_statement_impl(self) -> Optional[ASTNode]:
        """Реальная реализация parse_statement"""
        token = self.current_token()
        
        # Pass statement
        if token.type == TokenType.PASS:
            pass_token = self.advance()
            return Pass(line=pass_token.line, column=pass_token.column)
        
        # Break statement
        if token.type == TokenType.BREAK:
            break_token = self.advance()
            return Break(line=break_token.line, column=break_token.column)
        
        # Continue statement
        if token.type == TokenType.CONTINUE:
            cont_token = self.advance()
            return Continue(line=cont_token.line, column=cont_token.column)
        
        # Определение функции
        if token.type == TokenType.DEF:
            return self._parse_function_def()
        
        # Определение класса
        if token.type == TokenType.CLASS:
            return self._parse_class_def()
        
        # Условный оператор
        if token.type == TokenType.IF:
            return self._parse_if()
        
        # Цикл while
        if token.type == TokenType.WHILE:
            return self._parse_while()
        
        # Цикл for
        if token.type == TokenType.FOR:
            return self._parse_for()
        
        # Print (только Python 2)
        if token.type == TokenType.PRINT:
            return self._parse_print()
        
        # Return
        if token.type == TokenType.RETURN:
            return self._parse_return()
        
        # Import
        if token.type == TokenType.IMPORT:
            return self._parse_import()
        
        # From ... import
        if token.type == TokenType.FROM:
            return self._parse_from_import()
        
        # Присваивание или выражение
        return self._parse_expression_statement()
    
    def _parse_function_def(self) -> FunctionDef:
        """Разбор определения функции"""
        func_token = self.advance()  # def
        func_def = FunctionDef(line=func_token.line, column=func_token.column)
        
        # Имя функции
        name_token = self.expect(TokenType.IDENTIFIER)
        if name_token:
            func_def.name = name_token.value
        
        # Параметры
        self.expect(TokenType.LPAREN)
        
        if self.current_token().type != TokenType.RPAREN:
            while True:
                param_token = self.expect(TokenType.IDENTIFIER)
                if param_token:
                    func_def.params.append(param_token.value)
                
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                else:
                    break
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        # Тело функции
        self.expect(TokenType.INDENT)
        func_def.body = self._parse_block()
        self.expect(TokenType.DEDENT)
        
        return func_def
    
    def _parse_class_def(self) -> ClassDef:
        """Разбор определения класса"""
        class_token = self.advance()  # class
        class_def = ClassDef(line=class_token.line, column=class_token.column)
        
        # Имя класса
        name_token = self.expect(TokenType.IDENTIFIER)
        if name_token:
            class_def.name = name_token.value
        
        # Базовые классы (опционально)
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            
            if self.current_token().type != TokenType.RPAREN:
                while True:
                    base_token = self.expect(TokenType.IDENTIFIER)
                    if base_token:
                        class_def.bases.append(base_token.value)
                    
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
            
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        # Тело класса
        self.expect(TokenType.INDENT)
        class_def.body = self._parse_block()
        self.expect(TokenType.DEDENT)
        
        return class_def
    
    def _parse_if(self) -> If:
        """Разбор if/elif/else"""
        if_token = self.advance()  # if
        if_node = If(line=if_token.line, column=if_token.column)
        
        # Условие
        if_node.condition = self._parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        # Тело if
        self.expect(TokenType.INDENT)
        if_node.then_body = self._parse_block()
        self.expect(TokenType.DEDENT)
        
        # elif блоки
        while self.current_token().type == TokenType.ELIF:
            self.advance()  # elif
            elif_condition = self._parse_expression()
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            
            self.expect(TokenType.INDENT)
            elif_body = self._parse_block()
            self.expect(TokenType.DEDENT)
            
            if elif_condition is not None:  # Явная проверка на None
                if_node.elif_blocks.append((elif_condition, elif_body))
        
        # else блок
        if self.current_token().type == TokenType.ELSE:
            self.advance()  # else
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            
            self.expect(TokenType.INDENT)
            if_node.else_body = self._parse_block()
            self.expect(TokenType.DEDENT)
        
        return if_node
    
    def _parse_while(self) -> While:
        """Разбор цикла while"""
        while_token = self.advance()  # while
        while_node = While(line=while_token.line, column=while_token.column)
        
        # Условие
        while_node.condition = self._parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        # Тело цикла
        self.expect(TokenType.INDENT)
        while_node.body = self._parse_block()
        self.expect(TokenType.DEDENT)
        
        return while_node
    
    def _parse_for(self) -> For:
        """Разбор цикла for"""
        for_token = self.advance()  # for
        for_node = For(line=for_token.line, column=for_token.column)
        
        # Переменная цикла
        target_token = self.expect(TokenType.IDENTIFIER)
        if target_token:
            for_node.target = Name(id=target_token.value, line=target_token.line, column=target_token.column)
        
        self.expect(TokenType.IN)
        
        # Итерируемый объект
        for_node.iter = self._parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        # Тело цикла
        self.expect(TokenType.INDENT)
        for_node.body = self._parse_block()
        self.expect(TokenType.DEDENT)
        
        return for_node
    
    def _parse_print(self) -> Print:
        """Разбор оператора print (Python 2)"""
        print_token = self.advance()  # print
        print_node = Print(line=print_token.line, column=print_token.column)
        
        # Аргументы
        if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            while True:
                old_pos = self.pos
                arg = self._parse_expression()
                
                if arg is not None:  # Явная проверка на None
                    print_node.args.append(arg)
                
                # Защита от зацикливания
                if self.pos == old_pos:
                    break
                
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                    # Проверка на запятую в конце (без \n)
                    if self.current_token().type == TokenType.NEWLINE:
                        print_node.newline = False
                        break
                else:
                    break
        
        return print_node
    
    def _parse_return(self) -> Return:
        """Разбор оператора return"""
        return_token = self.advance()  # return
        return_node = Return(line=return_token.line, column=return_token.column)
        
        # Значение (опционально)
        if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            return_node.value = self._parse_expression()
        
        return return_node
    
    def _parse_import(self) -> Import:
        """Разбор import"""
        import_token = self.advance()  # import
        import_node = Import(line=import_token.line, column=import_token.column)
        
        # Модули
        while True:
            module_token = self.expect(TokenType.IDENTIFIER)
            if module_token:
                import_node.modules.append(module_token.value)
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return import_node
    
    def _parse_from_import(self) -> ImportFrom:
        """Разбор from ... import ..."""
        from_token = self.advance()  # from
        import_from = ImportFrom(line=from_token.line, column=from_token.column)
        
        # Модуль
        module_token = self.expect(TokenType.IDENTIFIER)
        if module_token:
            import_from.module = module_token.value
        
        self.expect(TokenType.IMPORT)
        
        # Имена
        while True:
            name_token = self.expect(TokenType.IDENTIFIER)
            if name_token:
                import_from.names.append(name_token.value)
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return import_from
    
    def _parse_expression_statement(self) -> Optional[ASTNode]:
        """Разбор выражения или присваивания"""
        expr = self._parse_expression()
        
        if expr is None:  # Явная проверка на None
            return None
        
        # Проверка на присваивание
        if self.current_token().type == TokenType.ASSIGN:
            self.advance()
            value = self._parse_expression()
            if value is not None:  # Явная проверка на None
                return Assign(target=expr, value=value, 
                             line=self.current_token().line, 
                             column=self.current_token().column)
            # Если значение не разобрано, возвращаем выражение
            return expr
        
        return expr
    
    def _parse_expression(self) -> Optional[ASTNode]:
        """Разбор выражения (точка входа)"""
        return self._parse_or_expr()
    
    def _parse_or_expr(self) -> Optional[ASTNode]:
        """Логическое OR"""
        left = self._parse_and_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        while self.current_token().type == TokenType.OR:
            op_token = self.advance()
            right = self._parse_and_expr()
            if right is not None:  # Явная проверка на None
                left = BinOp(left=left, op='or', right=right, 
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_and_expr(self) -> Optional[ASTNode]:
        """Логическое AND"""
        left = self._parse_not_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        while self.current_token().type == TokenType.AND:
            op_token = self.advance()
            right = self._parse_not_expr()
            if right is not None:  # Явная проверка на None
                left = BinOp(left=left, op='and', right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_not_expr(self) -> Optional[ASTNode]:
        """Логическое NOT"""
        if self.current_token().type == TokenType.NOT:
            op_token = self.advance()
            operand = self._parse_not_expr()
            if operand is not None:  # Явная проверка на None
                return UnaryOp(op='not', operand=operand,
                              line=op_token.line, column=op_token.column)
        
        return self._parse_comparison()
    
    def _parse_comparison(self) -> Optional[ASTNode]:
        """Сравнения"""
        left = self._parse_add_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        comp_ops = {TokenType.EQ, TokenType.NE, TokenType.LT, 
                   TokenType.LE, TokenType.GT, TokenType.GE, 
                   TokenType.IS, TokenType.IN}
        
        while self.current_token().type in comp_ops:
            op_token = self.advance()
            right = self._parse_add_expr()
            if right is not None:  # Явная проверка на None
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_add_expr(self) -> Optional[ASTNode]:
        """Сложение и вычитание"""
        left = self._parse_mult_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self._parse_mult_expr()
            if right is not None:  # Явная проверка на None
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_mult_expr(self) -> Optional[ASTNode]:
        """Умножение, деление, остаток"""
        left = self._parse_power_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        ops = {TokenType.MULTIPLY, TokenType.DIVIDE, 
               TokenType.FLOOR_DIVIDE, TokenType.MODULO}
        
        while self.current_token().type in ops:
            op_token = self.advance()
            right = self._parse_power_expr()
            if right is not None:  # Явная проверка на None
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_power_expr(self) -> Optional[ASTNode]:
        """Возведение в степень"""
        left = self._parse_unary_expr()
        
        if left is None:  # Явная проверка на None
            return None
        
        if self.current_token().type == TokenType.POWER:
            op_token = self.advance()
            right = self._parse_power_expr()  # Правоассоциативно
            if right is not None:  # Явная проверка на None
                return BinOp(left=left, op='**', right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def _parse_unary_expr(self) -> Optional[ASTNode]:
        """Унарные операторы"""
        if self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            operand = self._parse_unary_expr()
            if operand is not None:  # Явная проверка на None
                return UnaryOp(op=op_token.value, operand=operand,
                              line=op_token.line, column=op_token.column)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Optional[ASTNode]:
        """Первичные выражения"""
        token = self.current_token()
        
        # Идентификатор или вызов функции
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            name = Name(id=token.value, line=token.line, column=token.column)
            
            # Вызов функции
            if self.current_token().type == TokenType.LPAREN:
                self.advance()  # (
                call = Call(func=name, line=token.line, column=token.column)
                
                if self.current_token().type != TokenType.RPAREN:
                    while True:
                        old_pos = self.pos
                        arg = self._parse_expression()
                        
                        if arg is not None:  # Явная проверка на None
                            call.args.append(arg)
                        
                        # Защита от зацикливания
                        if self.pos == old_pos:
                            break
                        
                        if self.current_token().type == TokenType.COMMA:
                            self.advance()
                        else:
                            break
                
                self.expect(TokenType.RPAREN)
                return call
            
            return name
        
        # Числа
        if token.type == TokenType.NUMBER:
            self.advance()
            return Literal(value=token.value, line=token.line, column=token.column)
        
        # Строки
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(value=token.value, line=token.line, column=token.column)
        
        # Логические константы
        if token.type in (TokenType.TRUE, TokenType.FALSE, TokenType.NONE):
            self.advance()
            # Преобразуем значение
            if token.type == TokenType.TRUE:
                value = True
            elif token.type == TokenType.FALSE:
                value = False
            else:  # NONE
                value = None
            return Literal(value=value, line=token.line, column=token.column)
        
        # Скобки
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self._parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.errors.append(
            f"Строка {token.line}:{token.column}: "
            f"Неожиданный токен {token.type.name} (value={repr(token.value)})"
        )
        # Принудительное продвижение для предотвращения зацикливания
        self.advance()
        return None
    
    def _parse_block(self) -> List[ASTNode]:
        """Разбор блока кода"""
        statements = []
        
        while self.current_token().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            
            if self.current_token().type in (TokenType.DEDENT, TokenType.EOF):
                break
            
            # Сохраняем позицию для защиты от зацикливания
            old_pos = self.pos
            
            stmt = self._parse_statement()
            if stmt is not None:  # Явная проверка на None
                statements.append(stmt)
            
            # КРИТИЧЕСКИ ВАЖНО: если позиция не изменилась, принудительно продвигаемся
            if self.pos == old_pos:
                token = self.current_token()
                self.errors.append(
                    f"Строка {token.line}:{token.column}: "
                    f"Не удалось разобрать токен {token.type.name} (value={repr(token.value)}). "
                    f"Пропускаем для предотвращения зацикливания."
                )
                self.advance()
        
        return statements
