#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Узлы AST (абстрактного синтаксического дерева)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class ASTNode:
    """Базовый класс для всех узлов AST"""
    line: int = 0
    column: int = 0


@dataclass
class Program(ASTNode):
    """Корневой узел - программа"""
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class FunctionDef(ASTNode):
    """Определение функции"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassDef(ASTNode):
    """Определение класса"""
    name: str = ""
    bases: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class If(ASTNode):
    """Условный оператор"""
    condition: Optional[ASTNode] = None
    then_body: List[ASTNode] = field(default_factory=list)
    elif_blocks: List[tuple] = field(default_factory=list)  # (condition, body)
    else_body: List[ASTNode] = field(default_factory=list)


@dataclass
class While(ASTNode):
    """Цикл while"""
    condition: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class For(ASTNode):
    """Цикл for"""
    target: Optional[ASTNode] = None
    iter: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class Print(ASTNode):
    """Оператор print (Python 2)"""
    args: List[ASTNode] = field(default_factory=list)
    newline: bool = True


@dataclass
class Assign(ASTNode):
    """Присваивание"""
    target: Optional[ASTNode] = None
    value: Optional[ASTNode] = None


@dataclass
class BinOp(ASTNode):
    """Бинарная операция"""
    left: Optional[ASTNode] = None
    op: str = ""
    right: Optional[ASTNode] = None


@dataclass
class UnaryOp(ASTNode):
    """Унарная операция"""
    op: str = ""
    operand: Optional[ASTNode] = None


@dataclass
class Call(ASTNode):
    """Вызов функции"""
    func: Optional[ASTNode] = None
    args: List[ASTNode] = field(default_factory=list)


@dataclass
class Attribute(ASTNode):
    """Акцесс к атрибуту: obj.attr"""
    value: Optional[ASTNode] = None  # obj
    attr: str = ""  # название атрибута


@dataclass
class Subscript(ASTNode):
    """Оиндексация: obj[index]"""
    value: Optional[ASTNode] = None  # obj
    slice: Optional[ASTNode] = None  # index


@dataclass
class Return(ASTNode):
    """Оператор return"""
    value: Optional[ASTNode] = None


@dataclass
class Break(ASTNode):
    """Оператор break"""
    pass


@dataclass
class Continue(ASTNode):
    """Оператор continue"""
    pass


@dataclass
class Pass(ASTNode):
    """Оператор pass"""
    pass


@dataclass
class Name(ASTNode):
    """Идентификатор"""
    id: str = ""


@dataclass
class Literal(ASTNode):
    """Литерал (число, строка и т.д.)"""
    value: Any = None


@dataclass
class Import(ASTNode):
    """Оператор import"""
    modules: List[str] = field(default_factory=list)


@dataclass
class ImportFrom(ASTNode):
    """Оператор from ... import ..."""
    module: str = ""
    names: List[str] = field(default_factory=list)
