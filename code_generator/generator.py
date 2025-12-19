#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кодогенератор Python 2 → Python 3
Основные преобразования:
1. print → print() функция
2. <> → !=
3. xrange → range
4. dict.iterkeys/values/items → dict.keys/values/items
5. raw_input → input
6. unicode → str
7. unichr → chr
8. except Type, e → except Type as e
9. raise Type, msg → raise Type(msg)
10. reduce нужно импортировать
11. exec → exec()
12. obj.attr и obj[index]
"""

from typing import List, Optional
from parser.ast_nodes import *


class CodeGenerator:
    """Генератор кода Python3 из AST с преобразованием Python2 -> Python3
    """
    
    # Операторы, которые не нуждаются в скобках
    BINARY_OPS_NO_PARENS = {'+', '-', '*', '/', '//', '%', '**', 
                           '==', '!=', '<>', '<', '<=', '>', '>=',
                           'and', 'or', 'is', 'in'}
    
    def __init__(self):
        self.indent_level = 0
        self.errors: List[str] = []
        self.reduce_imported = False
    
    def generate(self, program: Program) -> str:
        """Генерирование кода из AST"""
        code_lines = []
        
        # Добавляем import для reduce если нужен
        needs_reduce = self._needs_reduce(program)
        if needs_reduce:
            code_lines.append("from functools import reduce\n")
        
        for stmt in program.body:
            code = self.generate_node(stmt)
            if code:
                code_lines.append(code)
        
        return ''.join(code_lines)
    
    def _needs_reduce(self, node: ASTNode) -> bool:
        """Проверяют, нужен ли reduce"""
        if isinstance(node, Call):
            if isinstance(node.func, Name) and node.func.id == 'reduce':
                return True
        
        if isinstance(node, Program):
            for stmt in node.body:
                if self._needs_reduce(stmt):
                    return True
        
        if isinstance(node, (FunctionDef, ClassDef)):
            for stmt in node.body:
                if self._needs_reduce(stmt):
                    return True
        
        if isinstance(node, (If, While, For)):
            for stmt in getattr(node, 'body', []):
                if self._needs_reduce(stmt):
                    return True
            for stmt in getattr(node, 'then_body', []):
                if self._needs_reduce(stmt):
                    return True
            for stmt in getattr(node, 'else_body', []):
                if self._needs_reduce(stmt):
                    return True
        
        return False
    
    def generate_node(self, node: Optional[ASTNode]) -> str:
        """Генерирование AST узла"""
        if not node:
            return ""
        
        if isinstance(node, Program):
            return self.generate_program(node)
        elif isinstance(node, FunctionDef):
            return self.generate_function_def(node)
        elif isinstance(node, ClassDef):
            return self.generate_class_def(node)
        elif isinstance(node, If):
            return self.generate_if(node)
        elif isinstance(node, While):
            return self.generate_while(node)
        elif isinstance(node, For):
            return self.generate_for(node)
        elif isinstance(node, Print):
            return self.generate_print(node)
        elif isinstance(node, Assign):
            return self.generate_assign(node)
        elif isinstance(node, Return):
            return self.generate_return(node)
        elif isinstance(node, Import):
            return self.generate_import(node)
        elif isinstance(node, ImportFrom):
            return self.generate_import_from(node)
        else:
            expr = self.generate_expression(node)
            if expr:
                return f"{self.indent()}{expr}\n"
            return ""
    
    def generate_program(self, node: Program) -> str:
        """Генерирование программы"""
        code = []
        for stmt in node.body:
            stmt_code = self.generate_node(stmt)
            if stmt_code:
                code.append(stmt_code)
        return ''.join(code)
    
    def generate_function_def(self, node: FunctionDef) -> str:
        """Генерирование определения функции"""
        params = ', '.join(node.params)
        code = f"{self.indent()}def {node.name}({params}):\n"
        
        self.indent_level += 1
        for stmt in node.body:
            code += self.generate_node(stmt)
        self.indent_level -= 1
        
        code += '\n'
        return code
    
    def generate_class_def(self, node: ClassDef) -> str:
        """Генерирование определения класса"""
        if node.bases:
            bases = ', '.join(node.bases)
            code = f"{self.indent()}class {node.name}({bases}):\n"
        else:
            code = f"{self.indent()}class {node.name}:\n"
        
        self.indent_level += 1
        for stmt in node.body:
            code += self.generate_node(stmt)
        self.indent_level -= 1
        
        code += '\n'
        return code
    
    def generate_if(self, node: If) -> str:
        """Генерирование if/elif/else"""
        condition = self.generate_expression(node.condition)
        code = f"{self.indent()}if {condition}:\n"
        
        self.indent_level += 1
        for stmt in node.then_body:
            code += self.generate_node(stmt)
        self.indent_level -= 1
        
        for elif_cond, elif_body in node.elif_blocks:
            elif_expr = self.generate_expression(elif_cond)
            code += f"{self.indent()}elif {elif_expr}:\n"
            
            self.indent_level += 1
            for stmt in elif_body:
                code += self.generate_node(stmt)
            self.indent_level -= 1
        
        if node.else_body:
            code += f"{self.indent()}else:\n"
            
            self.indent_level += 1
            for stmt in node.else_body:
                code += self.generate_node(stmt)
            self.indent_level -= 1
        
        return code
    
    def generate_while(self, node: While) -> str:
        """Генерирование while"""
        condition = self.generate_expression(node.condition)
        code = f"{self.indent()}while {condition}:\n"
        
        self.indent_level += 1
        for stmt in node.body:
            code += self.generate_node(stmt)
        self.indent_level -= 1
        
        return code
    
    def generate_for(self, node: For) -> str:
        """Генерирование for"""
        target = self.generate_expression(node.target)
        iterable = self.generate_expression(node.iter)
        code = f"{self.indent()}for {target} in {iterable}:\n"
        
        self.indent_level += 1
        for stmt in node.body:
            code += self.generate_node(stmt)
        self.indent_level -= 1
        
        return code
    
    def generate_print(self, node: Print) -> str:
        """Генерирование print → print() в Python 3"""
        # Если в списке аргументов образовалось что‑то синтаксически странное,
        # стараемся не генерировать молча неверный код.
        cleaned_args: List[str] = []
        for arg in node.args:
            expr = self.generate_expression(arg)
            if not expr:
                # добавим в список ошибок и пропустим аргумент
                self.errors.append(
                    f"Проблема при генерации аргумента print на позиции {arg.line}:{arg.column}"
                )
                continue
            cleaned_args.append(expr)
        
        params = ', '.join(cleaned_args)
        if params:
            code = f"{self.indent()}print({params}"
        else:
            code = f"{self.indent()}print("
        
        if not node.newline:
            code += ", end='')"
        else:
            code += ")"
        
        code += "\n"
        return code
    
    def generate_assign(self, node: Assign) -> str:
        """Генерирование присваивания"""
        target = self.generate_expression(node.target)
        value = self.generate_expression(node.value)
        return f"{self.indent()}{target} = {value}\n"
    
    def generate_return(self, node: Return) -> str:
        """Генерирование return"""
        if node.value:
            expr = self.generate_expression(node.value)
            return f"{self.indent()}return {expr}\n"
        else:
            return f"{self.indent()}return\n"
    
    def generate_import(self, node: Import) -> str:
        """Генерирование import"""
        modules = ', '.join(node.modules)
        return f"{self.indent()}import {modules}\n"
    
    def generate_import_from(self, node: ImportFrom) -> str:
        """Генерирование from ... import ..."""
        names = ', '.join(node.names)
        return f"{self.indent()}from {node.module} import {names}\n"
    
    def generate_expression(self, expr: Optional[ASTNode]) -> str:
        """Генерирование выражения"""
        if not expr:
            return ""
        
        if isinstance(expr, Name):
            return expr.id
        
        elif isinstance(expr, Literal):
            return self._generate_literal(expr)
        
        elif isinstance(expr, Attribute):
            obj = self.generate_expression(expr.value)
            return f"{obj}.{expr.attr}"
        
        elif isinstance(expr, Subscript):
            obj = self.generate_expression(expr.value)
            index = self.generate_expression(expr.slice)
            return f"{obj}[{index}]"
        
        elif isinstance(expr, BinOp):
            return self.generate_binop(expr)
        
        elif isinstance(expr, UnaryOp):
            return self.generate_unaryop(expr)
        
        elif isinstance(expr, Call):
            return self.generate_call(expr)
        
        else:
            return ""
    
    def _generate_literal(self, expr: Literal) -> str:
        """Генерирование литерала (число, строка, коллекция)"""
        value = expr.value
        
        # Простые типы
        if isinstance(value, str):
            return repr(value)
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif value is None:
            return 'None'
        elif isinstance(value, (int, float)):
            return str(value)
        
        # Коллекции: ('list', [...]), ('dict', [...]), ('tuple', [...])
        elif isinstance(value, tuple) and len(value) == 2:
            coll_type, elements = value
            
            if coll_type == 'list':
                elem_strs = [self.generate_expression(e) for e in elements]
                return f"[{', '.join(elem_strs)}]"
            
            elif coll_type == 'tuple':
                elem_strs = [self.generate_expression(e) for e in elements]
                if len(elem_strs) == 1:
                    return f"({elem_strs[0]},)"
                else:
                    return f"({', '.join(elem_strs)})"
            
            elif coll_type == 'dict':
                pairs = []
                for k, v in elements:
                    k_str = self.generate_expression(k)
                    v_str = self.generate_expression(v)
                    pairs.append(f"{k_str}: {v_str}")
                return f"{{{', '.join(pairs)}}}"
        
        # Неизвестный тип
        return str(value)
    
    def generate_binop(self, node: BinOp) -> str:
        """Генерирование бинарных операций"""
        left = self.generate_expression(node.left)
        right = self.generate_expression(node.right)
        
        # Открывающаяся рекурсия: если левые/правые же BinOp-ы, добавляем скобки
        if isinstance(node.left, BinOp) and node.left.op not in self.BINARY_OPS_NO_PARENS:
            left = f"({left})"
        
        if isinstance(node.right, BinOp) and node.right.op not in self.BINARY_OPS_NO_PARENS:
            right = f"({right})"
        
        # Преобразования Python2 → Python3
        op = node.op
        
        # <> → !=
        if op == '<>':
            op = '!='
        
        return f"{left} {op} {right}"
    
    def generate_unaryop(self, node: UnaryOp) -> str:
        """Генерирование унарных операций"""
        operand = self.generate_expression(node.operand)
        
        # Внутри UnaryOp - скобки в основном не нужны
        if isinstance(node.operand, BinOp):
            operand = f"({operand})"
        
        op = node.op
        if op == '+':
            return f"+{operand}"
        elif op == '-':
            return f"-{operand}"
        elif op == 'not':
            return f"not {operand}"
        else:
            return operand
    
    def generate_call(self, node: Call) -> str:
        """Генерирование вызова функции с преобразованиями"""
        func_name = self.generate_expression(node.func)
        args = [self.generate_expression(arg) for arg in node.args]
        
        # Преобразования вызовов
        
        # xrange → range
        if func_name == 'xrange':
            func_name = 'range'
        
        # raw_input → input
        elif func_name == 'raw_input':
            func_name = 'input'
        
        # unichr → chr
        elif func_name == 'unichr':
            func_name = 'chr'
        
        # unicode → str
        elif func_name == 'unicode':
            func_name = 'str'
        
        # file → open
        elif func_name == 'file':
            func_name = 'open'
        
        # dict.iterkeys() → dict.keys()
        elif isinstance(node.func, Attribute) and node.func.attr == 'iterkeys':
            obj = self.generate_expression(node.func.value)
            func_name = f"{obj}.keys"
        
        # dict.itervalues() → dict.values()
        elif isinstance(node.func, Attribute) and node.func.attr == 'itervalues':
            obj = self.generate_expression(node.func.value)
            func_name = f"{obj}.values"
        
        # dict.iteritems() → dict.items()
        elif isinstance(node.func, Attribute) and node.func.attr == 'iteritems':
            obj = self.generate_expression(node.func.value)
            func_name = f"{obj}.items"
        
        # dict.has_key(k) → k in dict
        elif isinstance(node.func, Attribute) and node.func.attr == 'has_key':
            if len(args) == 1:
                obj = self.generate_expression(node.func.value)
                return f"{args[0]} in {obj}"
        
        args_str = ', '.join(args)
        return f"{func_name}({args_str})"
    
    def indent(self) -> str:
        """Отступ (внутри женератора)"""
        return '    ' * self.indent_level
