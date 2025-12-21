#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Семантический анализатор для Python 2/3
"""

from typing import List, Set, Optional, Dict, Tuple
from parser.ast_nodes import (
    ASTNode, Program, FunctionDef, ClassDef, If, While, For,
    Return, Break, Continue, Assign, Call, Name, BinOp, Literal,
    Print, Import, ImportFrom, Pass, UnaryOp, Attribute, Subscript
)
from .errors import SemanticError, SemanticWarning, ErrorType


# Встроенные функции с их сигнатурами (имя: количество обязательных аргументов или None если переменное)
BUILTIN_FUNCTIONS = {
    'print': None,          # print(*args, **kwargs)
    'range': (1, 3),        # range(stop) или range(start, stop[, step])
    'xrange': (1, 3),       # xrange(stop) или xrange(start, stop[, step])
    'len': 1,               # len(obj)
    'str': 1,               # str(obj)
    'int': (0, 2),          # int([x[, base]])
    'float': 1,             # float(obj)
    'bool': (0, 1),         # bool([x])
    'list': (0, 1),         # list([iterable])
    'dict': (0, 1),         # dict([**kwargs])
    'set': (0, 1),          # set([iterable])
    'tuple': (0, 1),         # tuple([iterable])
    'type': 1,              # type(obj)
    'isinstance': 2,        # isinstance(obj, classinfo)
    'max': (1, None),       # max(arg1, arg2, *args)
    'min': (1, None),       # min(arg1, arg2, *args)
    'sum': (1, 2),          # sum(iterable[, start])
    'sorted': (1, 1),       # sorted(iterable)
    'reversed': 1,          # reversed(seq)
    'enumerate': (1, 2),    # enumerate(iterable[, start])
    'zip': (1, None),       # zip(iterable1[, iterable2, ...])
    'map': (2, None),       # map(func, *iterables)
    'filter': 2,            # filter(func, iterable)
    'input': (0, 1),        # input([prompt])
    'raw_input': (0, 1),    # raw_input([prompt])
    'open': (1, 3),         # open(filename[, mode[, buffering]])
    'file': (1, 3),         # file(filename[, mode[, buffering]])
    'abs': 1,               # abs(number)
    'round': (1, 2),        # round(number[, ndigits])
    'pow': (2, 3),          # pow(base, exp[, mod])
    'all': 1,               # all(iterable)
    'any': 1,               # any(iterable)
    'ord': 1,               # ord(char)
    'chr': 1,               # chr(i)
    'unichr': 1,            # unichr(i)
    'bin': 1,               # bin(number)
    'hex': 1,               # hex(number)
    'oct': 1,               # oct(number)
}

BUILTIN_TYPES = {
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    'type', 'object', 'bytes', 'bytearray', 'unicode', 'long'
}


class Scope:
    """Область видимости"""
    
    def __init__(self, name: str, parent: Optional['Scope'] = None, scope_type: str = 'global'):
        self.name = name
        self.parent = parent
        self.scope_type = scope_type  # 'global', 'function', 'class'
        self.declared_vars: Set[str] = set()
        self.functions: Dict[str, FunctionDef] = {}
        self.classes: Dict[str, ClassDef] = {}
        self.class_methods: Dict[str, Dict[str, FunctionDef]] = {}  # class_name -> {method_name -> FunctionDef}
        self.class_attributes: Dict[str, Set[str]] = {}  # class_name -> {attribute_names}
        self.in_loop = False
        self.in_function = False
        self.has_return = False
    
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
    
    def get_class(self, name: str) -> Optional[ClassDef]:
        """Получить определение класса из текущего или родительских скопов"""
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class(name)
        return None
    
    def get_class_methods(self, class_name: str) -> Optional[Dict[str, FunctionDef]]:
        """Получить методы класса"""
        if class_name in self.class_methods:
            return self.class_methods[class_name]
        if self.parent:
            return self.parent.get_class_methods(class_name)
        return None
    
    def get_class_attributes(self, class_name: str) -> Optional[Set[str]]:
        """Получить атрибуты класса"""
        if class_name in self.class_attributes:
            return self.class_attributes[class_name]
        if self.parent:
            return self.parent.get_class_attributes(class_name)
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
        self.global_scope = Scope('global', scope_type='global')
        self.current_scope = self.global_scope
        
        # Регистрирую встроенные функции
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
        
        elif isinstance(node, Attribute):
            self._analyze_attribute(node)
        
        elif isinstance(node, Subscript):
            self._analyze_subscript(node)
        
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
        func_scope = Scope(f"function_{node.name}", self.current_scope, 'function')
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
        self.current_scope.classes[node.name] = node
        
        # Инициализирую хранилище методов и атрибутов
        self.current_scope.class_methods[node.name] = {}
        self.current_scope.class_attributes[node.name] = set()
        
        # Создаю новый скоп для класса
        class_scope = Scope(f"class_{node.name}", self.current_scope, 'class')
        
        prev_scope = self.current_scope
        self.current_scope = class_scope
        
        # Анализирую тело класса
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                # Это метод класса
                self.current_scope.functions[stmt.name] = stmt
                prev_scope.class_methods[node.name][stmt.name] = stmt
                # Анализирую метод
                self._analyze_function_def(stmt)
            elif isinstance(stmt, Assign):
                # Это атрибут класса
                if isinstance(stmt.target, Name):
                    prev_scope.class_attributes[node.name].add(stmt.target.id)
                self._analyze_node(stmt)
            else:
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
            
            # Проверяю встроенные функции
            if func_name in BUILTIN_FUNCTIONS:
                # Проверяю количество аргументов
                arg_spec = BUILTIN_FUNCTIONS[func_name]
                if arg_spec is not None:
                    if isinstance(arg_spec, int):
                        # Точное число аргументов
                        if len(node.args) != arg_spec:
                            self.errors.append(SemanticError(
                                ErrorType.ARGUMENT_COUNT_MISMATCH,
                                f"Функция '{func_name}' ожидает {arg_spec} аргумент(ов), получено {len(node.args)}",
                                node.line,
                                node.column
                            ))
                    elif isinstance(arg_spec, tuple):
                        # Диапазон аргументов (min, max) или (min, None)
                        min_args, max_args = arg_spec
                        if len(node.args) < min_args:
                            self.errors.append(SemanticError(
                                ErrorType.ARGUMENT_COUNT_MISMATCH,
                                f"Функция '{func_name}' ожидает как минимум {min_args} аргумент(ов), получено {len(node.args)}",
                                node.line,
                                node.column
                            ))
                        elif max_args is not None and len(node.args) > max_args:
                            self.errors.append(SemanticError(
                                ErrorType.ARGUMENT_COUNT_MISMATCH,
                                f"Функция '{func_name}' ожидает максимум {max_args} аргумент(ов), получено {len(node.args)}",
                                node.line,
                                node.column
                            ))
            else:
                # Проверяю определённые функции
                func_def = self.current_scope.get_function(func_name)
                
                if func_name not in BUILTIN_FUNCTIONS and not func_def:
                    if not self.current_scope.is_declared(func_name):
                        self.errors.append(SemanticError(
                            ErrorType.UNDECLARED_IDENTIFIER,
                            f"Функция '{func_name}' не определена",
                            node.line,
                            node.column
                        ))
                
                # Проверяю количество аргументов определённой функции
                if func_def:
                    if len(node.args) != len(func_def.params):
                        self.errors.append(SemanticError(
                            ErrorType.ARGUMENT_COUNT_MISMATCH,
                            f"Функция '{func_name}' ожидает {len(func_def.params)} аргумент(ов), получено {len(node.args)}",
                            node.line,
                            node.column
                        ))
        elif isinstance(node.func, Attribute):
            # Вызов метода
            self._analyze_method_call(node)
        
        # Анализирую аргументы
        for arg in node.args:
            self._analyze_node(arg)
    
    def _analyze_method_call(self, node: Call):
        """Анализ вызова метода"""
        if isinstance(node.func, Attribute):
            obj_name = None
            class_name = None
            method_name = node.func.attr
            
            # Получаю имя объекта
            if isinstance(node.func.value, Name):
                obj_name = node.func.value.id
                # Проверяю, это класс или переменная класса
                class_def = self.current_scope.get_class(obj_name)
                if class_def:
                    class_name = obj_name
                else:
                    # Предполагаю, что это экземпляр какого-то класса
                    # Но мы не можем точно определить тип без анализа типов
                    pass
            
            # Если знаю класс, проверяю метод
            if class_name:
                class_methods = self.current_scope.get_class_methods(class_name)
                if class_methods and method_name in class_methods:
                    method_def = class_methods[method_name]
                    # Проверяю количество аргументов (учитываю self)
                    expected_args = len(method_def.params) - 1  # Исключаю self
                    if len(node.args) != expected_args:
                        self.errors.append(SemanticError(
                            ErrorType.ARGUMENT_COUNT_MISMATCH,
                            f"Метод '{method_name}' класса '{class_name}' ожидает {expected_args} аргумент(ов), получено {len(node.args)}",
                            node.line,
                            node.column
                        ))
    
    def _analyze_name(self, node: Name):
        """Анализ идентификатора"""
        if not self.current_scope.is_declared(node.id):
            # Проверяю если то встроенные
            if node.id not in BUILTIN_FUNCTIONS and node.id not in BUILTIN_TYPES:
                self.errors.append(SemanticError(
                    ErrorType.UNDECLARED_IDENTIFIER,
                    f"Переменная '{node.id}' не определена",
                    node.line,
                    node.column
                ))
    
    def _analyze_attribute(self, node: Attribute):
        """Анализ атрибута объекта"""
        # Анализирую объект
        self._analyze_node(node.value)
        
        # Проверяю атрибут
        if isinstance(node.value, Name):
            obj_name = node.value.id
            attr_name = node.attr
            
            # Проверяю, является ли объект классом
            class_def = self.current_scope.get_class(obj_name)
            if class_def:
                # Проверяю, есть ли такой атрибут или метод в классе
                class_methods = self.current_scope.get_class_methods(obj_name)
                class_attrs = self.current_scope.get_class_attributes(obj_name)
                
                if (not (class_methods and attr_name in class_methods) and 
                    not (class_attrs and attr_name in class_attrs)):
                    # Атрибут не найден
                    pass  # Допускаю динамические атрибуты в Python
    
    def _analyze_subscript(self, node: Subscript):
        """Анализ индексирования"""
        # Анализирую объект
        self._analyze_node(node.value)
        # Анализирую индекс
        self._analyze_node(node.index)
    
    def _analyze_binop(self, node: BinOp):
        """Анализ бинарных операций"""
        self._analyze_node(node.left)
        self._analyze_node(node.right)
        
        # Проверяю деление на ноль
        if node.op in ('/', '//'):
            if isinstance(node.right, Literal) and node.right.value == 0:
                self.errors.append(SemanticError(
                    ErrorType.CONST_DIVISION_BY_ZERO,
                    "Деление на ноль (константа)",
                    node.line,
                    node.column
                ))
