#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ноды AST (абстрактного синтаксического дерева)
Вариант 12 - с методами вывода
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class ASTNode:
    """Базовый класс для всех узлов AST"""
    line: int = 0
    column: int = 0
    
    def ast_to_string(self, indent: int = 0) -> str:
        """Преформатированый вывод узла (оверрайд в нижних классах)"""
        return " " * (indent * 2) + self.__class__.__name__


@dataclass
class Program(ASTNode):
    """Корневой узел - программа"""
    body: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [super().ast_to_string(indent)]
        for stmt in self.body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 1))
        return "\n".join(result)


@dataclass
class FunctionDef(ASTNode):
    """Определение функции"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}FunctionDef: name='{self.name}', params={self.params}"]
        for stmt in self.body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 1))
        return "\n".join(result)


@dataclass
class ClassDef(ASTNode):
    """Определение класса"""
    name: str = ""
    bases: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}ClassDef: name='{self.name}', bases={self.bases}"]
        for stmt in self.body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 1))
        return "\n".join(result)


@dataclass
class If(ASTNode):
    """Условный оператор"""
    condition: Optional[ASTNode] = None
    then_body: List[ASTNode] = field(default_factory=list)
    elif_blocks: List[tuple] = field(default_factory=list)  # (condition, body)
    else_body: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}If"]
        if self.condition:
            result.append(f"{' ' * ((indent + 1) * 2)}condition:")
            result.append(self.condition.ast_to_string(indent + 2))
        result.append(f"{' ' * ((indent + 1) * 2)}then_body:")
        for stmt in self.then_body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 2))
        for i, (elif_cond, elif_body) in enumerate(self.elif_blocks):
            result.append(f"{' ' * ((indent + 1) * 2)}elif_{i}:")
            if elif_cond:
                result.append(f"{' ' * ((indent + 2) * 2)}condition:")
                result.append(elif_cond.ast_to_string(indent + 3))
            result.append(f"{' ' * ((indent + 2) * 2)}body:")
            for stmt in elif_body:
                if stmt:
                    result.append(stmt.ast_to_string(indent + 3))
        if self.else_body:
            result.append(f"{' ' * ((indent + 1) * 2)}else_body:")
            for stmt in self.else_body:
                if stmt:
                    result.append(stmt.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class While(ASTNode):
    """Цикл while"""
    condition: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}While"]
        if self.condition:
            result.append(f"{' ' * ((indent + 1) * 2)}condition:")
            result.append(self.condition.ast_to_string(indent + 2))
        result.append(f"{' ' * ((indent + 1) * 2)}body:")
        for stmt in self.body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class For(ASTNode):
    """Цикл for"""
    target: Optional[ASTNode] = None
    iter: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}For"]
        if self.target:
            result.append(f"{' ' * ((indent + 1) * 2)}target:")
            result.append(self.target.ast_to_string(indent + 2))
        if self.iter:
            result.append(f"{' ' * ((indent + 1) * 2)}iter:")
            result.append(self.iter.ast_to_string(indent + 2))
        result.append(f"{' ' * ((indent + 1) * 2)}body:")
        for stmt in self.body:
            if stmt:
                result.append(stmt.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class Print(ASTNode):
    """Оператор print (Python 2)"""
    args: List[ASTNode] = field(default_factory=list)
    newline: bool = True
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}Print: newline={self.newline}"]
        if self.args:
            result.append(f"{' ' * ((indent + 1) * 2)}args:")
            for arg in self.args:
                if arg:
                    result.append(arg.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class Assign(ASTNode):
    """Присваивание"""
    target: Optional[ASTNode] = None
    value: Optional[ASTNode] = None
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}Assign"]
        if self.target:
            result.append(f"{' ' * ((indent + 1) * 2)}target:")
            result.append(self.target.ast_to_string(indent + 2))
        if self.value:
            result.append(f"{' ' * ((indent + 1) * 2)}value:")
            result.append(self.value.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class BinOp(ASTNode):
    """Бинарная операция"""
    left: Optional[ASTNode] = None
    op: str = ""
    right: Optional[ASTNode] = None
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}BinOp: op='{self.op}'"]
        if self.left:
            result.append(f"{' ' * ((indent + 1) * 2)}left:")
            result.append(self.left.ast_to_string(indent + 2))
        if self.right:
            result.append(f"{' ' * ((indent + 1) * 2)}right:")
            result.append(self.right.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class UnaryOp(ASTNode):
    """Унарная операция"""
    op: str = ""
    operand: Optional[ASTNode] = None
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}UnaryOp: op='{self.op}'"]
        if self.operand:
            result.append(self.operand.ast_to_string(indent + 1))
        return "\n".join(result)


@dataclass
class Call(ASTNode):
    """Вызов функции"""
    func: Optional[ASTNode] = None
    args: List[ASTNode] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}Call"]
        if self.func:
            result.append(f"{' ' * ((indent + 1) * 2)}func:")
            result.append(self.func.ast_to_string(indent + 2))
        if self.args:
            result.append(f"{' ' * ((indent + 1) * 2)}args:")
            for arg in self.args:
                if arg:
                    result.append(arg.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class Return(ASTNode):
    """Оператор return"""
    value: Optional[ASTNode] = None
    
    def ast_to_string(self, indent: int = 0) -> str:
        result = [f"{' ' * (indent * 2)}Return"]
        if self.value:
            result.append(f"{' ' * ((indent + 1) * 2)}value:")
            result.append(self.value.ast_to_string(indent + 2))
        return "\n".join(result)


@dataclass
class Name(ASTNode):
    """Идентификатор"""
    id: str = ""
    
    def ast_to_string(self, indent: int = 0) -> str:
        return f"{' ' * (indent * 2)}Name: id='{self.id}'"


@dataclass
class Literal(ASTNode):
    """Литерал (число, строка и т.д.)"""
    value: Any = None
    
    def ast_to_string(self, indent: int = 0) -> str:
        if isinstance(self.value, str):
            val_repr = f"'{self.value}'"
        else:
            val_repr = str(self.value)
        return f"{' ' * (indent * 2)}Literal: value={val_repr}"


@dataclass
class Import(ASTNode):
    """Оператор import"""
    modules: List[str] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        return f"{' ' * (indent * 2)}Import: modules={self.modules}"


@dataclass
class ImportFrom(ASTNode):
    """Оператор from ... import ..."""
    module: str = ""
    names: List[str] = field(default_factory=list)
    
    def ast_to_string(self, indent: int = 0) -> str:
        return f"{' ' * (indent * 2)}ImportFrom: module='{self.module}', names={self.names}"
