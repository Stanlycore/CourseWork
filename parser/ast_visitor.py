#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Посетитель AST для правильной визуализации дерева синтаксического разбора.
Отделяет условия, тело цикла, блоки if/elif/else в соответствии со структурой узла.
Правильно отображает Attribute, Subscript и коллекции.
"""

from typing import List, Tuple, Optional
from .ast_nodes import (
    ASTNode, Program, FunctionDef, ClassDef, If, While, For,
    Print, Assign, BinOp, UnaryOp, Call, Return, Name, Literal,
    Import, ImportFrom, Attribute, Subscript
)


class TreeNode:
    """Node for parse tree visualization"""
    
    def __init__(self, name: str, value: str = "", node_type: str = "default"):
        self.name = name
        self.value = value
        self.node_type = node_type  # default, keyword, operator, operand, condition, body
        self.children: List[TreeNode] = []
    
    def add_child(self, child: 'TreeNode'):
        self.children.append(child)
    
    def __repr__(self) -> str:
        val_str = f" '{self.value}'" if self.value else ""
        return f"{self.name}{val_str}"


class ASTToTreeVisitor:
    """Преобразует AST в структурированное дерево для визуализации"""
    
    def visit(self, node: ASTNode) -> Optional[TreeNode]:
        """Основной метод обхода"""
        if node is None:
            return None
        
        if isinstance(node, Program):
            return self._visit_program(node)
        elif isinstance(node, FunctionDef):
            return self._visit_function_def(node)
        elif isinstance(node, ClassDef):
            return self._visit_class_def(node)
        elif isinstance(node, If):
            return self._visit_if(node)
        elif isinstance(node, While):
            return self._visit_while(node)
        elif isinstance(node, For):
            return self._visit_for(node)
        elif isinstance(node, Print):
            return self._visit_print(node)
        elif isinstance(node, Return):
            return self._visit_return(node)
        elif isinstance(node, Assign):
            return self._visit_assign(node)
        elif isinstance(node, BinOp):
            return self._visit_binop(node)
        elif isinstance(node, UnaryOp):
            return self._visit_unaryop(node)
        elif isinstance(node, Call):
            return self._visit_call(node)
        elif isinstance(node, Attribute):
            return self._visit_attribute(node)
        elif isinstance(node, Subscript):
            return self._visit_subscript(node)
        elif isinstance(node, Name):
            return self._visit_name(node)
        elif isinstance(node, Literal):
            return self._visit_literal(node)
        elif isinstance(node, Import):
            return self._visit_import(node)
        elif isinstance(node, ImportFrom):
            return self._visit_import_from(node)
        
        return TreeNode(type(node).__name__)
    
    def _visit_program(self, node: Program) -> TreeNode:
        root = TreeNode("Program", node_type="default")
        for stmt in node.body:
            child = self.visit(stmt)
            if child:
                root.add_child(child)
        return root
    
    def _visit_function_def(self, node: FunctionDef) -> TreeNode:
        root = TreeNode("FunctionDef", value=node.name, node_type="keyword")
        
        # Parameters
        if node.params:
            params_node = TreeNode("Parameters", node_type="default")
            for param in node.params:
                params_node.add_child(TreeNode("Param", value=param, node_type="operand"))
            root.add_child(params_node)
        
        # Body
        if node.body:
            body_node = TreeNode("Body", node_type="default")
            for stmt in node.body:
                child = self.visit(stmt)
                if child:
                    body_node.add_child(child)
            root.add_child(body_node)
        
        return root
    
    def _visit_class_def(self, node: ClassDef) -> TreeNode:
        root = TreeNode("ClassDef", value=node.name, node_type="keyword")
        
        # Base classes
        if node.bases:
            bases_node = TreeNode("Bases", node_type="default")
            for base in node.bases:
                bases_node.add_child(TreeNode("Base", value=base, node_type="operand"))
            root.add_child(bases_node)
        
        # Body
        if node.body:
            body_node = TreeNode("Body", node_type="default")
            for stmt in node.body:
                child = self.visit(stmt)
                if child:
                    body_node.add_child(child)
            root.add_child(body_node)
        
        return root
    
    def _visit_if(self, node: If) -> TreeNode:
        """If/elif/else with separate conditions and body blocks"""
        root = TreeNode("If", node_type="keyword")
        
        # If condition and body
        if node.condition:
            cond_node = TreeNode("Condition", node_type="condition")
            cond_expr = self.visit(node.condition)
            if cond_expr:
                cond_node.add_child(cond_expr)
            root.add_child(cond_node)
        
        if node.then_body:
            body_node = TreeNode("Then", node_type="default")
            for stmt in node.then_body:
                child = self.visit(stmt)
                if child:
                    body_node.add_child(child)
            root.add_child(body_node)
        
        # Elif blocks
        for elif_cond, elif_body in node.elif_blocks:
            elif_node = TreeNode("Elif", node_type="keyword")
            
            if elif_cond:
                elif_cond_node = TreeNode("Condition", node_type="condition")
                cond_expr = self.visit(elif_cond)
                if cond_expr:
                    elif_cond_node.add_child(cond_expr)
                elif_node.add_child(elif_cond_node)
            
            if elif_body:
                elif_body_node = TreeNode("Then", node_type="default")
                for stmt in elif_body:
                    child = self.visit(stmt)
                    if child:
                        elif_body_node.add_child(child)
                elif_node.add_child(elif_body_node)
            
            root.add_child(elif_node)
        
        # Else block
        if node.else_body:
            else_node = TreeNode("Else", node_type="keyword")
            for stmt in node.else_body:
                child = self.visit(stmt)
                if child:
                    else_node.add_child(child)
            root.add_child(else_node)
        
        return root
    
    def _visit_while(self, node: While) -> TreeNode:
        """While with separated condition and body"""
        root = TreeNode("While", node_type="keyword")
        
        # Condition
        if node.condition:
            cond_node = TreeNode("Condition", node_type="condition")
            cond_expr = self.visit(node.condition)
            if cond_expr:
                cond_node.add_child(cond_expr)
            root.add_child(cond_node)
        
        # Body
        if node.body:
            body_node = TreeNode("Body", node_type="default")
            for stmt in node.body:
                child = self.visit(stmt)
                if child:
                    body_node.add_child(child)
            root.add_child(body_node)
        
        return root
    
    def _visit_for(self, node: For) -> TreeNode:
        """For with separated variable, iterator, and body"""
        root = TreeNode("For", node_type="keyword")
        
        # Loop variable
        if node.target:
            target_node = TreeNode("Target", node_type="condition")
            target_expr = self.visit(node.target)
            if target_expr:
                target_node.add_child(target_expr)
            root.add_child(target_node)
        
        # Iterator
        if node.iter:
            iter_node = TreeNode("Iterator", node_type="condition")
            iter_expr = self.visit(node.iter)
            if iter_expr:
                iter_node.add_child(iter_expr)
            root.add_child(iter_node)
        
        # Body
        if node.body:
            body_node = TreeNode("Body", node_type="default")
            for stmt in node.body:
                child = self.visit(stmt)
                if child:
                    body_node.add_child(child)
            root.add_child(body_node)
        
        return root
    
    def _visit_print(self, node: Print) -> TreeNode:
        root = TreeNode("Print", node_type="keyword")
        
        for arg in node.args:
            child = self.visit(arg)
            if child:
                root.add_child(child)
        
        if not node.newline:
            root.add_child(TreeNode("Modifier", value="no_newline", node_type="default"))
        
        return root
    
    def _visit_return(self, node: Return) -> TreeNode:
        root = TreeNode("Return", node_type="keyword")
        
        if node.value:
            child = self.visit(node.value)
            if child:
                root.add_child(child)
        
        return root
    
    def _visit_assign(self, node: Assign) -> TreeNode:
        root = TreeNode("Assign", node_type="operator")
        
        if node.target:
            target_node = TreeNode("Target", node_type="default")
            target_expr = self.visit(node.target)
            if target_expr:
                target_node.add_child(target_expr)
            root.add_child(target_node)
        
        if node.value:
            value_node = TreeNode("Value", node_type="default")
            value_expr = self.visit(node.value)
            if value_expr:
                value_node.add_child(value_expr)
            root.add_child(value_node)
        
        return root
    
    def _visit_binop(self, node: BinOp) -> TreeNode:
        root = TreeNode("BinOp", value=node.op, node_type="operator")
        
        if node.left:
            left_node = TreeNode("Left", node_type="default")
            left_expr = self.visit(node.left)
            if left_expr:
                left_node.add_child(left_expr)
            root.add_child(left_node)
        
        if node.right:
            right_node = TreeNode("Right", node_type="default")
            right_expr = self.visit(node.right)
            if right_expr:
                right_node.add_child(right_expr)
            root.add_child(right_node)
        
        return root
    
    def _visit_unaryop(self, node: UnaryOp) -> TreeNode:
        root = TreeNode("UnaryOp", value=node.op, node_type="operator")
        
        if node.operand:
            operand_node = TreeNode("Operand", node_type="default")
            operand_expr = self.visit(node.operand)
            if operand_expr:
                operand_node.add_child(operand_expr)
            root.add_child(operand_node)
        
        return root
    
    def _visit_call(self, node: Call) -> TreeNode:
        root = TreeNode("Call", node_type="operator")
        
        if node.func:
            func_node = TreeNode("Function", node_type="default")
            func_expr = self.visit(node.func)
            if func_expr:
                func_node.add_child(func_expr)
            root.add_child(func_node)
        
        if node.args:
            args_node = TreeNode("Arguments", node_type="default")
            for arg in node.args:
                arg_expr = self.visit(arg)
                if arg_expr:
                    args_node.add_child(arg_expr)
            root.add_child(args_node)
        
        return root
    
    def _visit_attribute(self, node: Attribute) -> TreeNode:
        """Обработка Attribute (obj.attr)
        Отображает объект и атрибут отдельно
        """
        root = TreeNode("Attribute", value=node.attr, node_type="operator")
        
        # Object
        if node.value:
            obj_node = TreeNode("Object", node_type="default")
            obj_expr = self.visit(node.value)
            if obj_expr:
                obj_node.add_child(obj_expr)
            root.add_child(obj_node)
        
        # Attribute name as separate node
        attr_node = TreeNode("AttrName", value=node.attr, node_type="operand")
        root.add_child(attr_node)
        
        return root
    
    def _visit_subscript(self, node: Subscript) -> TreeNode:
        """Обработка Subscript (obj[index])
        Отображает объект и индекс отдельно
        """
        root = TreeNode("Subscript", node_type="operator")
        
        # Object
        if node.value:
            obj_node = TreeNode("Object", node_type="default")
            obj_expr = self.visit(node.value)
            if obj_expr:
                obj_node.add_child(obj_expr)
            root.add_child(obj_node)
        
        # Index
        if node.slice:
            index_node = TreeNode("Index", node_type="default")
            index_expr = self.visit(node.slice)
            if index_expr:
                index_node.add_child(index_expr)
            root.add_child(index_node)
        
        return root
    
    def _visit_name(self, node: Name) -> TreeNode:
        return TreeNode("Name", value=node.id, node_type="operand")
    
    def _visit_literal(self, node: Literal) -> TreeNode:
        """Обработка литералов, включая коллекции"""
        value = node.value
        
        # Простые типы
        if isinstance(value, str):
            return TreeNode("Literal", value=repr(value)[:30], node_type="operand")
        elif isinstance(value, bool):
            return TreeNode("Literal", value=str(value), node_type="operand")
        elif value is None:
            return TreeNode("Literal", value="None", node_type="operand")
        elif isinstance(value, (int, float)):
            return TreeNode("Literal", value=str(value), node_type="operand")
        
        # Коллекции: ('list', [...]), ('dict', [...]), ('tuple', [...])
        elif isinstance(value, tuple) and len(value) == 2:
            coll_type, elements = value
            
            if coll_type == 'list':
                root = TreeNode("List", node_type="operator")
                for i, elem in enumerate(elements):
                    elem_node = TreeNode(f"Element[{i}]", node_type="default")
                    elem_expr = self.visit(elem)
                    if elem_expr:
                        elem_node.add_child(elem_expr)
                    root.add_child(elem_node)
                return root
            
            elif coll_type == 'tuple':
                root = TreeNode("Tuple", node_type="operator")
                for i, elem in enumerate(elements):
                    elem_node = TreeNode(f"Element[{i}]", node_type="default")
                    elem_expr = self.visit(elem)
                    if elem_expr:
                        elem_node.add_child(elem_expr)
                    root.add_child(elem_node)
                return root
            
            elif coll_type == 'dict':
                root = TreeNode("Dict", node_type="operator")
                for i, (k, v) in enumerate(elements):
                    pair_node = TreeNode(f"Pair[{i}]", node_type="default")
                    
                    key_node = TreeNode("Key", node_type="default")
                    key_expr = self.visit(k)
                    if key_expr:
                        key_node.add_child(key_expr)
                    pair_node.add_child(key_node)
                    
                    val_node = TreeNode("Value", node_type="default")
                    val_expr = self.visit(v)
                    if val_expr:
                        val_node.add_child(val_expr)
                    pair_node.add_child(val_node)
                    
                    root.add_child(pair_node)
                return root
        
        # Остальные
        val_str = str(value)[:30]
        if len(str(value)) > 30:
            val_str += "..."
        return TreeNode("Literal", value=val_str, node_type="operand")
    
    def _visit_import(self, node: Import) -> TreeNode:
        root = TreeNode("Import", node_type="keyword")
        
        for module in node.modules:
            root.add_child(TreeNode("Module", value=module, node_type="operand"))
        
        return root
    
    def _visit_import_from(self, node: ImportFrom) -> TreeNode:
        root = TreeNode("ImportFrom", value=node.module, node_type="keyword")
        
        for name in node.names:
            root.add_child(TreeNode("Name", value=name, node_type="operand"))
        
        return root
