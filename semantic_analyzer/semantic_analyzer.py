#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Семантический анализатор для Python 2/3
"""

from typing import List, Set, Optional, Dict, Tuple
from parser.ast_nodes import (
    ASTNode, Program, FunctionDef, ClassDef, If, While, For,
    Return, Break, Continue, Assign, Call, Name, BinOp, Literal,
    Print, Import, ImportFrom, Pass, UnaryOp
)
from .errors import SemanticError, SemanticWarning, ErrorType


BUILTIN_FUNCTIONS = {
    'print', 'range', 'xrange', 'len', 'str', 'int', 'float', 'bool',
    'list', 'dict', 'set', 'tuple', 'type', 'isinstance', 'max', 'min',
    'sum', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
    'input', 'raw_input', 'open', 'file', 'abs', 'round', 'pow',
    'all', 'any', 'ord', 'chr', 'unichr', 'bin', 'hex', 'oct'
}

BUILTIN_TYPES = {
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    'type', 'object', 'bytes', 'bytearray', 'unicode', 'long'
}


class Scope:
    """Область видимости"""
    
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.declared_vars: Set[str] = set()
        self.functions: Dict[str, FunctionDef] = {}
        self.in_loop = False
        self.in_function = False
    
    def declare(self, name: str) -> bool:
        """Объявить переменную в текущем скопе"""
        if name in self.declared_vars:
            return False  # Already declared
        self.declared_vars.add(name)
        return True
    
    def is_declared(self, name: str) -> bool:
        """Проверить, объявлена ли переменная в текущем или родительским скопах"""
        if name in self.declared_vars:
            return True
        if self.parent:
            return self.parent.is_declared(name)
        return False
    
    def get_function(self, name: str) -> Optional[FunctionDef]:
        """Получить определение функции из текущего или родительских скопов"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None


class SemanticAnalyzer:
    """Семантический анализатор для Python 2/3"""
    
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticWarning] = []
        self.current_scope: Optional[Scope] = None
        self.global_scope: Optional[Scope] = None
    
    def analyze(self, ast: ASTNode) -> List[SemanticError]:
        """Основная функция анализа"""
        self.errors = []
        self.warnings = []
        
        # Создаю глобальный скоп
        self.global_scope = Scope('global')
        self.current_scope = self.global_scope
        
        # Нрегистрирую встроенные функции
        for builtin in BUILTIN_FUNCTIONS:
            self.current_scope.declare(builtin)
        
        # Анализирую AST
        self._analyze_node(ast)
        
        return self.errors
    
    def _analyze_node(self, node: Optional[ASTNode]):
        """Анализ одного AST узла"""
        if node is None:
            return
        
        if isinstance(node, Program):
            for stmt in node.body:
                self._analyze_node(stmt)
        
        elif isinstance(node, FunctionDef):
            self._analyze_function_def(node)
        
        elif isinstance(node, ClassDef):
            self._analyze_class_def(node)
        
        elif isinstance(node, If):
            self._analyze_if(node)
        
        elif isinstance(node, While):
            self._analyze_while(node)
        
        elif isinstance(node, For):
            self._analyze_for(node)
        
        elif isinstance(node, Return):
            self._analyze_return(node)
        
        elif isinstance(node, Break):
            self._analyze_break(node)
        
        elif isinstance(node, Continue):
            self._analyze_continue(node)
        
        elif isinstance(node, Assign):
            self._analyze_assign(node)
        
        elif isinstance(node, Call):
            self._analyze_call(node)
        
        elif isinstance(node, Name):
            self._analyze_name(node)
        
        elif isinstance(node, BinOp):
            self._analyze_binop(node)
        
        elif isinstance(node, (Print, Import, ImportFrom, Pass)):
            # Эти не нуждаются в семантическом анализе
            pass
    
    def _analyze_function_def(self, node: FunctionDef):
        """Анализ определения функции"""
        # Проверяю на дублирование параметров
        param_names = set()
        for param in node.params:
            if param in param_names:
                self.errors.append(SemanticError(
                    ErrorType.DUPLICATE_ARGUMENT,
                    f"Параметр '{param}' дублируется в определении функции",
                    node.line,
                    node.column
                ))
            param_names.add(param)
        
        # Объявляю функцию в текущем скопе
        self.current_scope.functions[node.name] = node
        
        # Создаю новый скоп для функции
        func_scope = Scope(f"function_{node.name}", self.current_scope)
        func_scope.in_function = True
        
        # Объявляю параметры в скопе функции
        for param in node.params:
            func_scope.declare(param)
        
        # Сохраняю текущий скоп и переключаюсь на скоп функции
        prev_scope = self.current_scope
        self.current_scope = func_scope
        
        # Анализирую тело функции
        for stmt in node.body:
            self._analyze_node(stmt)
        
        # Восстанавливаю предыдущий скоп
        self.current_scope = prev_scope
    
    def _analyze_class_def(self, node: ClassDef):
        """Анализ определения класса"""
        # Объявляю класс в текущем скопе
        self.current_scope.declare(node.name)
        
        # Создаю новый скоп для класса
        class_scope = Scope(f"class_{node.name}", self.current_scope)
        
        prev_scope = self.current_scope
        self.current_scope = class_scope
        
        # Анализирую тело класса
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope = prev_scope
    
    def _analyze_if(self, node: If):
        """Анализ if стейтмента"""
        self._analyze_node(node.condition)
        
        for stmt in node.then_body:
            self._analyze_node(stmt)
        
        for condition, body in node.elif_blocks:
            self._analyze_node(condition)
            for stmt in body:
                self._analyze_node(stmt)
        
        for stmt in node.else_body:
            self._analyze_node(stmt)
    
    def _analyze_while(self, node: While):
        """Анализ while цикла"""
        self._analyze_node(node.condition)
        
        # Отмечаю контекст цикла
        prev_in_loop = self.current_scope.in_loop
        self.current_scope.in_loop = True
        
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope.in_loop = prev_in_loop
    
    def _analyze_for(self, node: For):
        """Анализ for цикла"""
        self._analyze_node(node.iter)
        
        # Объявляю переменную цикла
        if isinstance(node.target, Name):
            self.current_scope.declare(node.target.id)
        
        # Отмечаю контекст цикла
        prev_in_loop = self.current_scope.in_loop
        self.current_scope.in_loop = True
        
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope.in_loop = prev_in_loop
    
    def _analyze_return(self, node: Return):
        """Анализ return стейтмента"""
        if not self.current_scope.in_function:
            self.errors.append(SemanticError(
                ErrorType.RETURN_OUTSIDE_FUNCTION,
                "'return' вне функции",
                node.line,
                node.column
            ))
        
        if node.value:
            self._analyze_node(node.value)
    
    def _analyze_break(self, node: Break):
        """Анализ break стейтмента"""
        if not self.current_scope.in_loop:
            self.errors.append(SemanticError(
                ErrorType.BREAK_OUTSIDE_LOOP,
                "'break' вне цикла",
                node.line,
                node.column
            ))
    
    def _analyze_continue(self, node: Continue):
        """Анализ continue стейтмента"""
        if not self.current_scope.in_loop:
            self.errors.append(SemanticError(
                ErrorType.CONTINUE_OUTSIDE_LOOP,
                "'continue' вне цикла",
                node.line,
                node.column
            ))
    
    def _analyze_assign(self, node: Assign):
        """Анализ ассайнмент стейтмента"""
        # Проверяю наличие идентификатора
        if isinstance(node.target, Name):
            name = node.target.id
            
            # Проверяю переопределение встроенного типа
            if name in BUILTIN_TYPES:
                self.warnings.append(SemanticWarning(
                    ErrorType.REDEFINITION_BUILTIN,
                    f"Переопределение встроенного типа '{name}'",
                    node.line,
                    node.column
                ))
            
            # Объявляю или обновляю переменную
            self.current_scope.declare(name)
        
        # Анализирую значение
        self._analyze_node(node.value)
    
    def _analyze_call(self, node: Call):
        """Анализ вызова функции"""
        # Проверяю наличие функции
        if isinstance(node.func, Name):
            func_name = node.func.id
            
            # Проверяю в списке функций
            func_def = self.current_scope.get_function(func_name)
            
            if func_name not in BUILTIN_FUNCTIONS and not func_def:
                if not self.current_scope.is_declared(func_name):
                    self.errors.append(SemanticError(
                        ErrorType.UNDECLARED_IDENTIFIER,
                        f"Функция '{func_name}' не определена",
                        node.line,
                        node.column
                    ))
            
            # Проверяю количество аргументов
            if func_def:
                if len(node.args) != len(func_def.params):
                    self.errors.append(SemanticError(
                        ErrorType.ARGUMENT_COUNT_MISMATCH,
                        f"Функция '{func_name}' ожидает {len(func_def.params)} "
                        f"аргументов, получено {len(node.args)}",
                        node.line,
                        node.column
                    ))
        
        # Анализирую аргументы
        for arg in node.args:
            self._analyze_node(arg)
    
    def _analyze_name(self, node: Name):
        """Анализ идентификатора"""
        if not self.current_scope.is_declared(node.id):
            # Проверяю если то встроенные
            if node.id not in BUILTIN_FUNCTIONS:
                self.errors.append(SemanticError(
                    ErrorType.UNDECLARED_IDENTIFIER,
                    f"Переменная '{node.id}' не определена",
                    node.line,
                    node.column
                ))
    
    def _analyze_binop(self, node: BinOp):
        """Анализ бинарных операций"""
        self._analyze_node(node.left)
        self._analyze_node(node.right)
        
        # Проверяю деление на константный ноль
        if node.op in ('/', '//'):
            if isinstance(node.right, Literal) and node.right.value == 0:
                self.errors.append(SemanticError(
                    ErrorType.CONST_DIVISION_BY_ZERO,
                    "Деление на ноль (константа)",
                    node.line,
                    node.column
                ))
