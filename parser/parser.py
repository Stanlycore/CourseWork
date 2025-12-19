#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синтаксический анализатор Python
"""

from typing import List, Optional
from lexer import Token, TokenType
from .ast_nodes import *


class Parser:
    """Синтаксический анализатор Python с подробными ошибками"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[str] = []
    
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
            f"Ожидался {token_type.name}, но получен {token.type.name}"
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
            
            old_pos = self.pos
            stmt = self.parse_statement()
            if stmt:
                program.body.append(stmt)
            
            if self.pos == old_pos:
                token = self.current_token()
                self.errors.append(
                    f"Строка {token.line}:{token.column}: "
                    f"Не удалось разобрать инструкцию. Пропуск токена {token.type.name}."
                )
                self.advance()
        
        return program
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Разбор одной инструкции"""
        token = self.current_token()
        
        if token.type == TokenType.DEF:
            return self.parse_function_def()
        
        if token.type == TokenType.CLASS:
            return self.parse_class_def()
        
        if token.type == TokenType.IF:
            return self.parse_if()
        
        if token.type == TokenType.WHILE:
            return self.parse_while()
        
        if token.type == TokenType.FOR:
            return self.parse_for()
        
        if token.type == TokenType.PRINT:
            return self.parse_print()
        
        if token.type == TokenType.RETURN:
            return self.parse_return()
        
        if token.type == TokenType.IMPORT:
            return self.parse_import()
        
        if token.type == TokenType.FROM:
            return self.parse_from_import()
        
        return self.parse_expression_statement()
    
    def parse_function_def(self) -> FunctionDef:
        """Разбор определения функции"""
        func_token = self.advance()  # def
        func_def = FunctionDef(line=func_token.line, column=func_token.column)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        if name_token:
            func_def.name = name_token.value
        
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
        
        self.expect(TokenType.INDENT)
        func_def.body = self.parse_block()
        self.expect(TokenType.DEDENT)
        
        return func_def
    
    def parse_class_def(self) -> ClassDef:
        """Разбор определения класса"""
        class_token = self.advance()  # class
        class_def = ClassDef(line=class_token.line, column=class_token.column)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        if name_token:
            class_def.name = name_token.value
        
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
        
        self.expect(TokenType.INDENT)
        class_def.body = self.parse_block()
        self.expect(TokenType.DEDENT)
        
        return class_def
    
    def parse_if(self) -> If:
        """Разбор if/elif/else"""
        if_token = self.advance()  # if
        if_node = If(line=if_token.line, column=if_token.column)
        
        if_node.condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        self.expect(TokenType.INDENT)
        if_node.then_body = self.parse_block()
        self.expect(TokenType.DEDENT)
        
        while self.current_token().type == TokenType.ELIF:
            self.advance()  # elif
            elif_condition = self.parse_expression()
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            
            self.expect(TokenType.INDENT)
            elif_body = self.parse_block()
            self.expect(TokenType.DEDENT)
            
            if_node.elif_blocks.append((elif_condition, elif_body))
        
        if self.current_token().type == TokenType.ELSE:
            self.advance()  # else
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            
            self.expect(TokenType.INDENT)
            if_node.else_body = self.parse_block()
            self.expect(TokenType.DEDENT)
        
        return if_node
    
    def parse_while(self) -> While:
        """Разбор цикла while"""
        while_token = self.advance()  # while
        while_node = While(line=while_token.line, column=while_token.column)
        
        while_node.condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        self.expect(TokenType.INDENT)
        while_node.body = self.parse_block()
        self.expect(TokenType.DEDENT)
        
        return while_node
    
    def parse_for(self) -> For:
        """Разбор цикла for"""
        for_token = self.advance()  # for
        for_node = For(line=for_token.line, column=for_token.column)
        
        target_token = self.expect(TokenType.IDENTIFIER)
        if target_token:
            for_node.target = Name(id=target_token.value, line=target_token.line, column=target_token.column)
        
        self.expect(TokenType.IN)
        
        for_node.iter = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        
        self.expect(TokenType.INDENT)
        for_node.body = self.parse_block()
        self.expect(TokenType.DEDENT)
        
        return for_node
    
    def parse_print(self) -> Print:
        """Разбор оператора print (Python 2)
        
        Синтаксис: print [expr [, expr]*] [,]
        - expr, expr, expr  - выведет и новую строку
        - expr, expr,       - выведет БЕЗ новой строки (trailing comma)
        """
        print_token = self.advance()  # print
        print_node = Print(line=print_token.line, column=print_token.column)
        
        # Если после print сразу NEWLINE/EOF/DEDENT, то просто print()
        if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            return print_node
        
        # Разбираем список аргументов, разделённых запятыми
        while True:
            # Если токен - это что-то, что не может быть началом выражения
            # (например, NEWLINE, EOF, DEDENT, ключевое слово), выходим
            if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
                break
            
            # Пытаемся разобрать выражение
            arg = self.parse_expression()
            if arg:
                print_node.args.append(arg)
            else:
                # Если не удалось разобрать, значит синтаксическая ошибка
                token = self.current_token()
                self.errors.append(
                    f"Строка {token.line}:{token.column}: "
                    f"Ожидается выражение в print, но получен токен {token.type.name}"
                )
                break
            
            # Смотрим, что после выражения
            if self.current_token().type == TokenType.COMMA:
                self.advance()  # consume comma
                
                # Проверяем, не идёт ли после запятой конец инструкции
                # (это означает trailing comma)
                if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
                    print_node.newline = False  # trailing comma = no newline
                    break
                # Иначе ожидается ещё одно выражение (цикл продолжится)
            else:
                # Нет запятой - это конец списка аргументов
                # Проверяем, не стоит ли здесь неожиданный токен
                # (это ошибка вроде 'print value1 value2' без запятой)
                if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
                    token = self.current_token()
                    self.errors.append(
                        f"Строка {token.line}:{token.column}: "
                        f"Ожидается запятая или конец инструкции, но получен токен {token.type.name}. "
                        f"Возможно, в print забыли запятую между аргументами."
                    )
                break
        
        return print_node
    
    def parse_return(self) -> Return:
        """Разбор оператора return"""
        return_token = self.advance()  # return
        return_node = Return(line=return_token.line, column=return_token.column)
        
        if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            return_node.value = self.parse_expression()
        
        return return_node
    
    def parse_import(self) -> Import:
        """Разбор import"""
        import_token = self.advance()  # import
        import_node = Import(line=import_token.line, column=import_token.column)
        
        while True:
            module_token = self.expect(TokenType.IDENTIFIER)
            if module_token:
                import_node.modules.append(module_token.value)
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return import_node
    
    def parse_from_import(self) -> ImportFrom:
        """Разбор from ... import ..."""
        from_token = self.advance()  # from
        import_from = ImportFrom(line=from_token.line, column=from_token.column)
        
        module_token = self.expect(TokenType.IDENTIFIER)
        if module_token:
            import_from.module = module_token.value
        
        self.expect(TokenType.IMPORT)
        
        while True:
            name_token = self.expect(TokenType.IDENTIFIER)
            if name_token:
                import_from.names.append(name_token.value)
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return import_from
    
    def parse_expression_statement(self) -> Optional[ASTNode]:
        """Разбор выражения или присваивания"""
        expr = self.parse_expression()
        
        if not expr:
            return None
        
        if self.current_token().type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
            if value:
                return Assign(target=expr, value=value, 
                             line=self.current_token().line, 
                             column=self.current_token().column)
        
        return expr
    
    def parse_expression(self) -> Optional[ASTNode]:
        """Разбор выражения"""
        return self.parse_or_expr()
    
    def parse_or_expr(self) -> Optional[ASTNode]:
        """Логическое OR"""
        left = self.parse_and_expr()
        
        if not left:
            return None
        
        while self.current_token().type == TokenType.OR:
            op_token = self.advance()
            right = self.parse_and_expr()
            if right:
                left = BinOp(left=left, op='or', right=right, 
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_and_expr(self) -> Optional[ASTNode]:
        """Логическое AND"""
        left = self.parse_not_expr()
        
        if not left:
            return None
        
        while self.current_token().type == TokenType.AND:
            op_token = self.advance()
            right = self.parse_not_expr()
            if right:
                left = BinOp(left=left, op='and', right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_not_expr(self) -> Optional[ASTNode]:
        """Логическое NOT"""
        if self.current_token().type == TokenType.NOT:
            op_token = self.advance()
            operand = self.parse_not_expr()
            if operand:
                return UnaryOp(op='not', operand=operand,
                              line=op_token.line, column=op_token.column)
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> Optional[ASTNode]:
        """Сравнения"""
        left = self.parse_add_expr()
        
        if not left:
            return None
        
        comp_ops = {TokenType.EQ, TokenType.NE, TokenType.LT, 
                   TokenType.LE, TokenType.GT, TokenType.GE, 
                   TokenType.IS, TokenType.IN}
        
        while self.current_token().type in comp_ops:
            op_token = self.advance()
            right = self.parse_add_expr()
            if right:
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_add_expr(self) -> Optional[ASTNode]:
        """Сложение и вычитание"""
        left = self.parse_mult_expr()
        
        if not left:
            return None
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_mult_expr()
            if right:
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_mult_expr(self) -> Optional[ASTNode]:
        """Умножение, деление, остаток"""
        left = self.parse_power_expr()
        
        if not left:
            return None
        
        ops = {TokenType.MULTIPLY, TokenType.DIVIDE, 
               TokenType.FLOOR_DIVIDE, TokenType.MODULO}
        
        while self.current_token().type in ops:
            op_token = self.advance()
            right = self.parse_power_expr()
            if right:
                left = BinOp(left=left, op=op_token.value, right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_power_expr(self) -> Optional[ASTNode]:
        """Возведение в степень"""
        left = self.parse_unary_expr()
        
        if not left:
            return None
        
        if self.current_token().type == TokenType.POWER:
            op_token = self.advance()
            right = self.parse_power_expr()  # Правоассоциативно
            if right:
                return BinOp(left=left, op='**', right=right,
                            line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_unary_expr(self) -> Optional[ASTNode]:
        """Унарные операторы"""
        if self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            operand = self.parse_unary_expr()
            if operand:
                return UnaryOp(op=op_token.value, operand=operand,
                              line=op_token.line, column=op_token.column)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Optional[ASTNode]:
        """Постфиксные выражения (атрибуты, индексация, вызовы)"""
        expr = self.parse_primary()
        
        if not expr:
            return None
        
        while True:
            if self.current_token().type == TokenType.DOT:
                dot_token = self.current_token()
                self.advance()
                attr_token = self.expect(TokenType.IDENTIFIER)
                if attr_token:
                    expr = Attribute(value=expr, attr=attr_token.value,
                                   line=dot_token.line, column=dot_token.column)
                else:
                    break
            elif self.current_token().type == TokenType.LBRACKET:
                bracket_token = self.current_token()
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                if index:
                    expr = Subscript(value=expr, slice=index,
                                   line=bracket_token.line, column=bracket_token.column)
                else:
                    break
            elif self.current_token().type == TokenType.LPAREN:
                paren_token = self.current_token()
                self.advance()
                if isinstance(expr, Name):
                    call = Call(func=expr, line=paren_token.line, column=paren_token.column)
                    
                    if self.current_token().type != TokenType.RPAREN:
                        while True:
                            old_pos = self.pos
                            arg = self.parse_expression()
                            
                            if arg:
                                call.args.append(arg)
                            
                            if self.pos == old_pos:
                                break
                            
                            if self.current_token().type == TokenType.COMMA:
                                self.advance()
                            else:
                                break
                    
                    self.expect(TokenType.RPAREN)
                    expr = call
                elif isinstance(expr, Attribute):
                    call = Call(func=expr, line=paren_token.line, column=paren_token.column)
                    
                    if self.current_token().type != TokenType.RPAREN:
                        while True:
                            old_pos = self.pos
                            arg = self.parse_expression()
                            
                            if arg:
                                call.args.append(arg)
                            
                            if self.pos == old_pos:
                                break
                            
                            if self.current_token().type == TokenType.COMMA:
                                self.advance()
                            else:
                                break
                    
                    self.expect(TokenType.RPAREN)
                    expr = call
                else:
                    break
            else:
                break
        
        return expr
    
    def parse_primary(self) -> Optional[ASTNode]:
        """Первичные выражения"""
        token = self.current_token()
        
        # Идентификатор
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Name(id=token.value, line=token.line, column=token.column)
        
        # Число
        if token.type == TokenType.NUMBER:
            self.advance()
            return Literal(value=token.value, line=token.line, column=token.column)
        
        # Строка
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(value=token.value, line=token.line, column=token.column)
        
        # Логические значения
        if token.type in (TokenType.TRUE, TokenType.FALSE, TokenType.NONE):
            self.advance()
            if token.type == TokenType.TRUE:
                return Literal(value=True, line=token.line, column=token.column)
            elif token.type == TokenType.FALSE:
                return Literal(value=False, line=token.line, column=token.column)
            else:  # NONE
                return Literal(value=None, line=token.line, column=token.column)
        
        # Список [1, 2, 3]
        if token.type == TokenType.LBRACKET:
            bracket_token = token
            self.advance()
            elements = []
            
            while self.current_token().type != TokenType.RBRACKET:
                elem = self.parse_expression()
                if elem:
                    elements.append(elem)
                
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                else:
                    break
            
            self.expect(TokenType.RBRACKET)
            return Literal(value=('list', elements), line=bracket_token.line, column=bracket_token.column)
        
        # Словарь {"a": 1}
        if token.type == TokenType.LBRACE:
            brace_token = token
            self.advance()
            pairs = []
            
            while self.current_token().type != TokenType.RBRACE:
                key = self.parse_expression()
                if key:
                    self.expect(TokenType.COLON)
                    value = self.parse_expression()
                    if value:
                        pairs.append((key, value))
                
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                else:
                    break
            
            self.expect(TokenType.RBRACE)
            return Literal(value=('dict', pairs), line=brace_token.line, column=brace_token.column)
        
        # Кортеж (1, 2, 3) или (а) и скобки
        if token.type == TokenType.LPAREN:
            paren_token = token
            self.advance()
            
            # Пустые скобки
            if self.current_token().type == TokenType.RPAREN:
                self.advance()
                return Literal(value=('tuple', []), line=paren_token.line, column=paren_token.column)
            
            expr = self.parse_expression()
            
            # Кортеж со скобками
            if self.current_token().type == TokenType.COMMA:
                elements = [expr] if expr else []
                while self.current_token().type == TokenType.COMMA:
                    self.advance()
                    if self.current_token().type == TokenType.RPAREN:
                        break
                    elem = self.parse_expression()
                    if elem:
                        elements.append(elem)
                
                self.expect(TokenType.RPAREN)
                return Literal(value=('tuple', elements), line=paren_token.line, column=paren_token.column)
            else:
                # Простые скобки
                self.expect(TokenType.RPAREN)
                return expr
        
        self.errors.append(
            f"Строка {token.line}:{token.column}: "
            f"Неожиданный токен {token.type.name}"
        )
        self.advance()
        return None
    
    def parse_block(self) -> List[ASTNode]:
        """Разбор блока кода"""
        statements = []
        
        while self.current_token().type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            
            if self.current_token().type in (TokenType.DEDENT, TokenType.EOF):
                break
            
            old_pos = self.pos
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            if self.pos == old_pos:
                token = self.current_token()
                self.errors.append(
                    f"Строка {token.line}:{token.column}: "
                    f"Не удалось разобрать токен {token.type.name}. "
                    f"Пропускаем для предотвращения зацикливания."
                )
                self.advance()
        
        return statements
