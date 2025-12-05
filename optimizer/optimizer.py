#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизатор AST
"""

from parser.ast_nodes import *
from typing import Any


class Optimizer:
    """Оптимизатор абстрактного синтаксического дерева"""
    
    def __init__(self):
        self.optimizations_applied = 0
    
    def optimize(self, ast: ASTNode) -> ASTNode:
        """Главная функция оптимизации"""
        self.optimizations_applied = 0
        
        # Применяем оптимизации
        ast = self.constant_folding(ast)
        ast = self.dead_code_elimination(ast)
        
        return ast
    
    def constant_folding(self, node: ASTNode) -> ASTNode:
        """Свертывание констант"""
        if isinstance(node, Program):
            node.body = [self.constant_folding(stmt) for stmt in node.body]
            return node
        
        if isinstance(node, FunctionDef):
            node.body = [self.constant_folding(stmt) for stmt in node.body]
            return node
        
        if isinstance(node, If):
            node.condition = self.constant_folding(node.condition)
            node.then_body = [self.constant_folding(stmt) for stmt in node.then_body]
            node.elif_blocks = [(self.constant_folding(cond), [self.constant_folding(s) for s in body]) 
                               for cond, body in node.elif_blocks]
            node.else_body = [self.constant_folding(stmt) for stmt in node.else_body]
            return node
        
        if isinstance(node, While):
            node.condition = self.constant_folding(node.condition)
            node.body = [self.constant_folding(stmt) for stmt in node.body]
            return node
        
        if isinstance(node, For):
            node.iter = self.constant_folding(node.iter)
            node.body = [self.constant_folding(stmt) for stmt in node.body]
            return node
        
        if isinstance(node, Assign):
            node.value = self.constant_folding(node.value)
            return node
        
        if isinstance(node, BinOp):
            node.left = self.constant_folding(node.left)
            node.right = self.constant_folding(node.right)
            
            # Если оба операнда - литералы, вычисляем
            if isinstance(node.left, Literal) and isinstance(node.right, Literal):
                try:
                    result = self._evaluate_binop(node.left.value, node.op, node.right.value)
                    self.optimizations_applied += 1
                    return Literal(value=result, line=node.line, column=node.column)
                except:
                    pass  # Не удалось вычислить
            
            return node
        
        if isinstance(node, UnaryOp):
            node.operand = self.constant_folding(node.operand)
            
            if isinstance(node.operand, Literal):
                try:
                    result = self._evaluate_unaryop(node.op, node.operand.value)
                    self.optimizations_applied += 1
                    return Literal(value=result, line=node.line, column=node.column)
                except:
                    pass
            
            return node
        
        return node
    
    def _evaluate_binop(self, left: Any, op: str, right: Any) -> Any:
        """Вычисление бинарной операции"""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '//':
            return left // right
        elif op == '%':
            return left % right
        elif op == '**':
            return left ** right
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def _evaluate_unaryop(self, op: str, operand: Any) -> Any:
        """Вычисление унарной операции"""
        if op == '+':
            return +operand
        elif op == '-':
            return -operand
        elif op == 'not':
            return not operand
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def dead_code_elimination(self, node: ASTNode) -> ASTNode:
        """Удаление мертвого кода"""
        if isinstance(node, Program):
            node.body = [self.dead_code_elimination(stmt) for stmt in node.body 
                        if not self._is_dead_code(stmt)]
            return node
        
        if isinstance(node, FunctionDef):
            node.body = [self.dead_code_elimination(stmt) for stmt in node.body
                        if not self._is_dead_code(stmt)]
            return node
        
        if isinstance(node, If):
            # Если условие - константа, можно упростить
            if isinstance(node.condition, Literal):
                self.optimizations_applied += 1
                if node.condition.value:
                    # Условие всегда истинно - возвращаем then_body
                    result = Program(body=node.then_body)
                    return result
                else:
                    # Условие всегда ложно - проверяем elif и else
                    if node.elif_blocks:
                        # TODO: обработать elif
                        pass
                    if node.else_body:
                        result = Program(body=node.else_body)
                        return result
                    return Program(body=[])
            
            node.then_body = [self.dead_code_elimination(stmt) for stmt in node.then_body]
            node.elif_blocks = [(cond, [self.dead_code_elimination(s) for s in body])
                               for cond, body in node.elif_blocks]
            node.else_body = [self.dead_code_elimination(stmt) for stmt in node.else_body]
            return node
        
        if isinstance(node, While):
            node.body = [self.dead_code_elimination(stmt) for stmt in node.body]
            return node
        
        if isinstance(node, For):
            node.body = [self.dead_code_elimination(stmt) for stmt in node.body]
            return node
        
        return node
    
    def _is_dead_code(self, node: ASTNode) -> bool:
        """Проверка, является ли код мертвым"""
        # Простые критерии
        if isinstance(node, Program) and not node.body:
            return True
        
        # Можно добавить более сложные правила
        return False
