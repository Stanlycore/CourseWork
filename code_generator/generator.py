#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор Python3 кода из AST
"""

from parser.ast_nodes import *
from typing import List


class CodeGenerator:
    """Генератор Python3 кода"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  # 4 пробела
    
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
                lines.append(self._generate_statement(stmt))
        
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
                lines.append(self._generate_statement(stmt))
        
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
                lines.append(self._generate_statement(stmt))
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
                    lines.append(self._generate_statement(stmt))
            self.indent_level -= 1
        
        # else
        if node.else_body:
            lines.append(f"{self._indent()}else:")
            
            self.indent_level += 1
            for stmt in node.else_body:
                lines.append(self._generate_statement(stmt))
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
                lines.append(self._generate_statement(stmt))
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_for(self, node: For) -> str:
        """Генерация цикла for"""
        target = self._generate_expression(node.target)
        iter_expr = self._generate_expression(node.iter)
        lines = [f"{self._indent()}for {target} in {iter_expr}:"]
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                lines.append(self._generate_statement(stmt))
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _generate_print(self, node: Print) -> str:
        """Генерация print (Python 2 -> Python 3)"""
        args = ", ".join([self._generate_expression(arg) for arg in node.args])
        
        # Преобразование Python2 print в Python3 print()
        if not node.newline:
            return f"{self._indent()}print({args}, end='')"  # запятая в конце = без \n
        return f"{self._indent()}print({args})"
    
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
        if isinstance(node, Name):
            return node.id
        
        if isinstance(node, Literal):
            if isinstance(node.value, str):
                # Экранирование кавычек
                escaped = node.value.replace('"', '\\"')
                return f'"{escaped}"'
            return str(node.value)
        
        if isinstance(node, BinOp):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            return f"({left} {node.op} {right})"
        
        if isinstance(node, UnaryOp):
            operand = self._generate_expression(node.operand)
            return f"({node.op}{operand})"
        
        if isinstance(node, Call):
            func = self._generate_expression(node.func)
            args = ", ".join([self._generate_expression(arg) for arg in node.args])
            return f"{func}({args})"
        
        return "<unknown>"
