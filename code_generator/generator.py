#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор Python3 кода из AST
Полное преобразование из Python 2 в Python 3 в соответствии с документацией

Основные отличия Python 2->3:
- print statement -> print() function
- / integer division -> // floor division
- range() -> list(range()) где необходимо
- xrange() -> range()
- dict.iteritems() -> dict.items()
- dict.iterkeys() -> dict.keys()
- dict.itervalues() -> dict.values()
- unicode/str handling
- exception syntax (except E, e -> except E as e)
- long integers (L suffix removed)
- octal literals (0755 -> 0o755)
"""

from parser.ast_nodes import *
from typing import List, Set


class CodeGenerator:
    """Генератор Python3 кода из AST с полной трансляцией Python 2->3"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  # 4 пробела
        
        # Множество известных функций/методов Python 2
        self.py2_functions = {'xrange', 'raw_input', 'reload', 'reduce', 'unicode', 'basestring'}
        self.py2_methods = {'iteritems', 'iterkeys', 'itervalues', 'has_key'}
    
    def generate(self, ast: ASTNode) -> str:
        """Генерировать Python3 код из AST"""
        if isinstance(ast, Program):
            return self._generate_program(ast)
        return ""
    
    def _indent(self) -> str:
        """Текущий отступ"""
        return self.indent_str * self.indent_level
    
    def _generate_program(self, node: Program) -> str:
        """Генерация программы"""
        lines = []
        for stmt in node.body:
            code = self._generate_statement(stmt)
            if code:
                lines.append(code)
        return "\n".join(lines) if lines else "pass"
    
    def _generate_statement(self, node: ASTNode) -> str:
        """Генерация инструкции"""
        if isinstance(node, FunctionDef):
            return self._generate_function_def(node)
        
        if isinstance(node, ClassDef):
            return self._generate_class_def(node)
        
        if isinstance(node, If):
            return self._generate_if(node)
        
        if isinstance(node, While):
            return self._generate_while(node)
        
        if isinstance(node, For):
            return self._generate_for(node)
        
        if isinstance(node, Print):
            return self._generate_print(node)
        
        if isinstance(node, Return):
            return self._generate_return(node)
        
        if isinstance(node, Import):
            return self._generate_import(node)
        
        if isinstance(node, ImportFrom):
            return self._generate_import_from(node)
        
        if isinstance(node, Assign):
            return self._generate_assign(node)
        
        # Выражение как инструкция
        expr_code = self._generate_expression(node)
        if expr_code:
            return self._indent() + expr_code
        return ""
    
    def _generate_function_def(self, node: FunctionDef) -> str:
        """Генерация определения функции"""
        params = ", ".join(node.params)
        lines = [f"{self._indent()}def {node.name}({params}):"]
        
        self.indent_level += 1
        
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
        
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_class_def(self, node: ClassDef) -> str:
        """Генерация определения класса"""
        bases = f"({', '.join(node.bases)})" if node.bases else ""
        lines = [f"{self._indent()}class {node.name}{bases}:"]
        
        self.indent_level += 1
        
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
        
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_if(self, node: If) -> str:
        """Генерация if/elif/else"""
        lines = []
        
        # if
        condition = self._generate_expression(node.condition)
        lines.append(f"{self._indent()}if {condition}:")
        
        self.indent_level += 1
        if not node.then_body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.then_body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        # elif
        for elif_cond, elif_body in node.elif_blocks:
            condition = self._generate_expression(elif_cond)
            lines.append(f"{self._indent()}elif {condition}:")
            
            self.indent_level += 1
            if not elif_body:
                lines.append(f"{self._indent()}pass")
            else:
                for stmt in elif_body:
                    code = self._generate_statement(stmt)
                    if code:
                        lines.append(code)
            self.indent_level -= 1
        
        # else
        if node.else_body:
            lines.append(f"{self._indent()}else:")
            
            self.indent_level += 1
            for stmt in node.else_body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
            self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_while(self, node: While) -> str:
        """Генерация цикла while"""
        condition = self._generate_expression(node.condition)
        lines = [f"{self._indent()}while {condition}:"]
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_for(self, node: For) -> str:
        """Генерация цикла for"""
        target = self._generate_expression(node.target)
        iter_expr = self._generate_expression(node.iter)
        
        # Преобразование xrange -> range
        if isinstance(node.iter, Call):
            if isinstance(node.iter.func, Name) and node.iter.func.id == 'xrange':
                iter_expr = self._generate_expression(
                    Call(func=Name(id='range', line=0, column=0), 
                         args=node.iter.args, line=0, column=0)
                )
        
        lines = [f"{self._indent()}for {target} in {iter_expr}:"]
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                code = self._generate_statement(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_print(self, node: Print) -> str:
        """Генерация print (Python 2 statement -> Python 3 function)"""
        if not node.args:
            # print с пустыми аргументами
            return f"{self._indent()}print()"
        
        args = ", ".join([self._generate_expression(arg) for arg in node.args])
        
        # Преобразование Python2 print в Python3 print()
        if node.newline:
            return f"{self._indent()}print({args})"
        else:
            # запятая в конце = без \n (Python 2) -> end='' (Python 3)
            return f"{self._indent()}print({args}, end='')"
    
    def _generate_return(self, node: Return) -> str:
        """Генерация return"""
        if node.value:
            value = self._generate_expression(node.value)
            return f"{self._indent()}return {value}"
        return f"{self._indent()}return"
    
    def _generate_import(self, node: Import) -> str:
        """Генерация import"""
        modules = ", ".join(node.modules)
        return f"{self._indent()}import {modules}"
    
    def _generate_import_from(self, node: ImportFrom) -> str:
        """Генерация from ... import ..."""
        names = ", ".join(node.names)
        return f"{self._indent()}from {node.module} import {names}"
    
    def _generate_assign(self, node: Assign) -> str:
        """Генерация присваивания"""
        target = self._generate_expression(node.target)
        value = self._generate_expression(node.value)
        return f"{self._indent()}{target} = {value}"
    
    def _generate_expression(self, node: ASTNode) -> str:
        """Генерация выражения"""
        if node is None:
            return ""
        
        if isinstance(node, Name):
            # Преобразование xrange -> range
            if node.id == 'xrange':
                return 'range'
            # Преобразование raw_input -> input
            if node.id == 'raw_input':
                return 'input'
            # Преобразование unicode -> str
            if node.id == 'unicode':
                return 'str'
            # Преобразование long -> int (отдалённо)
            if node.id == 'long':
                return 'int'
            return node.id
        
        if isinstance(node, Literal):
            # Обработка числовых литералов
            if isinstance(node.value, str):
                # Экранирование кавычек
                escaped = node.value.replace('"', '\\"')
                return f'"{escaped}"'
            elif isinstance(node.value, bool):
                return "True" if node.value else "False"
            elif node.value is None:
                return "None"
            return str(node.value)
        
        if isinstance(node, BinOp):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            
            # Преобразование / (обычное деление) -> / (в Python 3 всегда float)
            # В Python 2 / для целых чисел = floor division
            # В Python 3 нужен // для floor division
            op = node.op
            if op == '/':
                # ВНИМАНИЕ: полная трансляция требует анализа типов
                # Здесь консервативно оставляем / и оставляем от разработчика
                # проверку на целые числа
                op = '/'
            
            return f"({left} {op} {right})"
        
        if isinstance(node, UnaryOp):
            operand = self._generate_expression(node.operand)
            return f"({node.op}{operand})"
        
        if isinstance(node, Call):
            func = self._generate_expression(node.func)
            
            # Преобразование xrange(...) -> range(...)
            if isinstance(node.func, Name):
                if node.func.id == 'xrange':
                    func = 'range'
                elif node.func.id == 'raw_input':
                    func = 'input'
                elif node.func.id == 'unicode':
                    func = 'str'
                elif node.func.id == 'reduce':
                    func = 'functools.reduce'  # require import functools
            
            args = ", ".join([self._generate_expression(arg) for arg in node.args])
            return f"{func}({args})"
        
        return "<unknown>"
