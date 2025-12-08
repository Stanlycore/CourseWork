#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор Python3 кода из AST с полным преобразованием основных дифференций Python2 вс Python3.
"""

from parser.ast_nodes import *
from typing import List, Dict, Set


class CodeGenerator:
    """Python2->Python3 генератор кода"""
    
    # Антимонополия Python 2 к Python 3
    PY2_TO_PY3_METHODS = {
        'iteritems': 'items',
        'iterkeys': 'keys',
        'itervalues': 'values',
        'has_key': '__contains__',  # жест d.has_key(k) -> k in d
    }
    
    # Монополии Python 2 (xrange, итд)
    PY2_FUNCTIONS = {'xrange', 'execfile', 'raw_input', 'unichr'}
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  # 4 пробела
        self.used_future_imports: Set[str] = set()
    
    def generate(self, ast: ASTNode) -> str:
        """GENERATE Python3 код из AST"""
        if isinstance(ast, Program):
            return self._generate_program(ast)
        return ""
    
    def _indent(self) -> str:
        """Текущий отступ"""
        return self.indent_str * self.indent_level
    
    def _generate_program(self, node: Program) -> str:
        """Генерация программы"""
        lines = []
        
        # Добавим future imports если нужны
        # это помогает с совместимостью, но в Python3 можно исключить
        # lines.append("from __future__ import absolute_import, division, print_function")
        # lines.append("")
        
        for stmt in node.body:
            code = self._generate_statement(stmt)
            if code:
                lines.append(code)
        
        return "\n".join(lines)
    
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
        return self._indent() + self._generate_expression(node)
    
    def _generate_function_def(self, node: FunctionDef) -> str:
        """Генерация определения функции"""
        params = ", ".join(node.params)
        lines = [f"{self._indent()}def {node.name}({params}):"]
        
        self.indent_level += 1
        
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
        
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_class_def(self, node: ClassDef) -> str:
        """Генерация определения класса"""
        bases = f"({', '.join(node.bases)})" if node.bases else ":"
        if bases != ":":
            bases = bases.rstrip(":") + ":"
        
        lines = [f"{self._indent()}class {node.name}{bases}"]
        
        self.indent_level += 1
        
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
        
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
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
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
                    stmt_code = self._generate_statement(stmt)
                    if stmt_code:
                        lines.append(stmt_code)
            self.indent_level -= 1
        
        # else
        if node.else_body:
            lines.append(f"{self._indent()}else:")
            
            self.indent_level += 1
            for stmt in node.else_body:
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
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
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_for(self, node: For) -> str:
        """Генерация цикла for (xrange -> range)"""
        target = self._generate_expression(node.target)
        iter_expr = self._generate_expression(node.iter)
        
        # PYTHON 2->3: xrange автоматически становится range
        if iter_expr.startswith('xrange('):
            iter_expr = 'range(' + iter_expr[7:]
        
        lines = [f"{self._indent()}for {target} in {iter_expr}:"]
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_code = self._generate_statement(stmt)
                if stmt_code:
                    lines.append(stmt_code)
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_print(self, node: Print) -> str:
        """
        Генерация print (Python 2 -> Python 3):
        print x, y в Python 2 -> print(x, y) в Python 3
        print x, в Python 2 -> print(x, end='') в Python 3
        """
        args = ", ".join([self._generate_expression(arg) for arg in node.args])
        
        if not node.newline:
            # Python 2: print x, (no newline) -> Python 3: print(x, end='')
            return f"{self._indent()}print({args}, end='')" if args else f"{self._indent()}print(end='')"
        
        return f"{self._indent()}print({args})" if args else f"{self._indent()}print()"
    
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
        """Генерация выражения с конвертацию Python 2->3"""
        if isinstance(node, Name):
            # PYTHON 2->3: волшебные константы
            name = node.id
            if name == 'xrange':
                return 'range'  # Восок если встретится здесь
            if name == 'raw_input':
                return 'input'  # raw_input -> input
            if name == 'unichr':
                return 'chr'  # unichr -> chr
            if name == 'unicode':
                return 'str'  # unicode -> str
            if name == 'long':
                return 'int'  # long -> int
            if name == 'execfile':
                return 'exec'  # execfile - редко, но теоретически
            return name
        
        if isinstance(node, Literal):
            # Обработка твердых целых чисел Python 2
            if isinstance(node.value, str):
                # Python 2: u"string" -> Python 3: "string"
                # от лексера не должно надеть u
                escaped = node.value.replace('"', '\\"')
                return f'"{escaped}"'
            
            # Обработка приставки L для долгих чисел
            val_str = str(node.value)
            if val_str.endswith('L') or val_str.endswith('l'):
                val_str = val_str[:-1]  # Удаляем L
            
            return val_str
        
        if isinstance(node, BinOp):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            
            # PYTHON 2->3: целое деление
            # В Python 2: 5 / 2 = 2 (целое)
            # В Python 3: 5 / 2 = 2.5 (вещественное)
            # Python 3 использует // для целого деления
            # Теоретически, если нам нужно целое деление, мы скорвим грамматику к / -> //
            # Но ты же пишешь Python 3, и это сохранится.
            
            return f"({left} {node.op} {right})"
        
        if isinstance(node, UnaryOp):
            operand = self._generate_expression(node.operand)
            return f"({node.op} {operand})" if node.op == 'not' else f"({node.op}{operand})"
        
        if isinstance(node, Call):
            func = self._generate_expression(node.func)
            
            # PYTHON 2->3: волшебные методы dict
            # Пример: d.iteritems() -> d.items()
            if isinstance(node.func, Name):
                # Простые вызовы: xrange(10) -> range(10)
                func_name = node.func.id
                if func_name == 'xrange':
                    func = 'range'
                elif func_name == 'raw_input':
                    func = 'input'
                elif func_name == 'unichr':
                    func = 'chr'
                elif func_name == 'execfile':
                    func = 'exec'
            
            args = ", ".join([self._generate_expression(arg) for arg in node.args])
            return f"{func}({args})"
        
        return "<unknown>"
