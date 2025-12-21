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
    """Representation области видимости"""
    
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.declared_vars: Set[str] = set()
        self.functions: Dict[str, FunctionDef] = {}
        self.in_loop = False
        self.in_function = False
    
    def declare(self, name: str) -> bool:
        """Declare a variable in current scope"""
        if name in self.declared_vars:
            return False  # Already declared
        self.declared_vars.add(name)
        return True
    
    def is_declared(self, name: str) -> bool:
        """Check if variable is declared in current or parent scopes"""
        if name in self.declared_vars:
            return True
        if self.parent:
            return self.parent.is_declared(name)
        return False
    
    def get_function(self, name: str) -> Optional[FunctionDef]:
        """Get function definition from current or parent scopes"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None


class SemanticAnalyzer:
    """Semantic analyzer for Python 2/3 code"""
    
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticWarning] = []
        self.current_scope: Optional[Scope] = None
        self.global_scope: Optional[Scope] = None
    
    def analyze(self, ast: ASTNode) -> List[SemanticError]:
        """Main analysis function"""
        self.errors = []
        self.warnings = []
        
        # Create global scope
        self.global_scope = Scope('global')
        self.current_scope = self.global_scope
        
        # Register built-in functions
        for builtin in BUILTIN_FUNCTIONS:
            self.current_scope.declare(builtin)
        
        # Analyze AST
        self._analyze_node(ast)
        
        return self.errors
    
    def _analyze_node(self, node: Optional[ASTNode]):
        """Analyze single AST node"""
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
            # These don't need semantic analysis
            pass
    
    def _analyze_function_def(self, node: FunctionDef):
        """Analyze function definition"""
        # Check for duplicate parameters
        param_names = set()
        for param in node.params:
            if param in param_names:
                self.errors.append(SemanticError(
                    ErrorType.DUPLICATE_ARGUMENT,
                    f"Parameter '{param}' is duplicated in function definition",
                    node.line,
                    node.column
                ))
            param_names.add(param)
        
        # Declare function in current scope
        self.current_scope.functions[node.name] = node
        
        # Create new scope for function
        func_scope = Scope(f"function_{node.name}", self.current_scope)
        func_scope.in_function = True
        
        # Declare parameters in function scope
        for param in node.params:
            func_scope.declare(param)
        
        # Save current scope and switch to function scope
        prev_scope = self.current_scope
        self.current_scope = func_scope
        
        # Analyze function body
        for stmt in node.body:
            self._analyze_node(stmt)
        
        # Restore previous scope
        self.current_scope = prev_scope
    
    def _analyze_class_def(self, node: ClassDef):
        """Analyze class definition"""
        # Declare class in current scope
        self.current_scope.declare(node.name)
        
        # Create new scope for class
        class_scope = Scope(f"class_{node.name}", self.current_scope)
        
        prev_scope = self.current_scope
        self.current_scope = class_scope
        
        # Analyze class body
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope = prev_scope
    
    def _analyze_if(self, node: If):
        """Analyze if statement"""
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
        """Analyze while loop"""
        self._analyze_node(node.condition)
        
        # Mark loop context
        prev_in_loop = self.current_scope.in_loop
        self.current_scope.in_loop = True
        
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope.in_loop = prev_in_loop
    
    def _analyze_for(self, node: For):
        """Analyze for loop"""
        self._analyze_node(node.iter)
        
        # Declare loop variable
        if isinstance(node.target, Name):
            self.current_scope.declare(node.target.id)
        
        # Mark loop context
        prev_in_loop = self.current_scope.in_loop
        self.current_scope.in_loop = True
        
        for stmt in node.body:
            self._analyze_node(stmt)
        
        self.current_scope.in_loop = prev_in_loop
    
    def _analyze_return(self, node: Return):
        """Analyze return statement"""
        if not self.current_scope.in_function:
            self.errors.append(SemanticError(
                ErrorType.RETURN_OUTSIDE_FUNCTION,
                "'return' outside function",
                node.line,
                node.column
            ))
        
        if node.value:
            self._analyze_node(node.value)
    
    def _analyze_break(self, node: Break):
        """Analyze break statement"""
        if not self.current_scope.in_loop:
            self.errors.append(SemanticError(
                ErrorType.BREAK_OUTSIDE_LOOP,
                "'break' outside loop",
                node.line,
                node.column
            ))
    
    def _analyze_continue(self, node: Continue):
        """Analyze continue statement"""
        if not self.current_scope.in_loop:
            self.errors.append(SemanticError(
                ErrorType.CONTINUE_OUTSIDE_LOOP,
                "'continue' outside loop",
                node.line,
                node.column
            ))
    
    def _analyze_assign(self, node: Assign):
        """Analyze assignment statement"""
        # Check if target is identifier
        if isinstance(node.target, Name):
            name = node.target.id
            
            # Check if redefining builtin
            if name in BUILTIN_TYPES:
                self.warnings.append(SemanticWarning(
                    ErrorType.REDEFINITION_BUILTIN,
                    f"Redefining built-in type '{name}'",
                    node.line,
                    node.column
                ))
            
            # Declare or update variable
            self.current_scope.declare(name)
        
        # Analyze value
        self._analyze_node(node.value)
    
    def _analyze_call(self, node: Call):
        """Analyze function call"""
        # Check if function exists
        if isinstance(node.func, Name):
            func_name = node.func.id
            
            # Check in user-defined functions
            func_def = self.current_scope.get_function(func_name)
            
            if func_name not in BUILTIN_FUNCTIONS and not func_def:
                if not self.current_scope.is_declared(func_name):
                    self.errors.append(SemanticError(
                        ErrorType.UNDECLARED_IDENTIFIER,
                        f"Function '{func_name}' is not defined",
                        node.line,
                        node.column
                    ))
            
            # Check argument count
            if func_def:
                if len(node.args) != len(func_def.params):
                    self.errors.append(SemanticError(
                        ErrorType.ARGUMENT_COUNT_MISMATCH,
                        f"Function '{func_name}' expects {len(func_def.params)} "
                        f"argument(s), got {len(node.args)}",
                        node.line,
                        node.column
                    ))
        
        # Analyze arguments
        for arg in node.args:
            self._analyze_node(arg)
    
    def _analyze_name(self, node: Name):
        """Analyze name (identifier) reference"""
        if not self.current_scope.is_declared(node.id):
            # Check if it's in builtins
            if node.id not in BUILTIN_FUNCTIONS:
                self.errors.append(SemanticError(
                    ErrorType.UNDECLARED_IDENTIFIER,
                    f"Name '{node.id}' is not defined",
                    node.line,
                    node.column
                ))
    
    def _analyze_binop(self, node: BinOp):
        """Analyze binary operation"""
        self._analyze_node(node.left)
        self._analyze_node(node.right)
        
        # Check for constant division by zero
        if node.op in ('/', '//'):
            if isinstance(node.right, Literal) and node.right.value == 0:
                self.errors.append(SemanticError(
                    ErrorType.CONST_DIVISION_BY_ZERO,
                    "Division by zero (constant)",
                    node.line,
                    node.column
                ))
