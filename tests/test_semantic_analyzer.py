#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты семантического анализатора
"""

import sys
import os

# Добавляем родительский директорий в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from semantic_analyzer.errors import ErrorType


class TestSemanticAnalyzer(unittest.TestCase):
    """Набор тестов семантического анализатора"""
    
    def setUp(self):
        """Preparation for each test"""
        self.analyzer = SemanticAnalyzer()
    
    def _analyze(self, source_code):
        """Helper to analyze code"""
        lexer = Lexer(source_code)
        tokens = lexer.scan()
        parser = Parser(tokens)
        ast = parser.parse()
        return self.analyzer.analyze(ast), ast
    
    def test_undeclared_identifier(self):
        """Test: Using undeclared variable"""
        code = "print(undefined_var)"
        errors, _ = self._analyze(code)
        
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_argument_count_mismatch(self):
        """Test: Function call with wrong number of arguments"""
        code = """def foo(a, b):
    pass

foo(1)
"""
        errors, _ = self._analyze(code)
        self.assertTrue(any(e.error_type == ErrorType.ARGUMENT_COUNT_MISMATCH for e in errors))
    
    def test_return_outside_function(self):
        """Test: return statement outside function"""
        code = "return 42"
        errors, _ = self._analyze(code)
        
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any(e.error_type == ErrorType.RETURN_OUTSIDE_FUNCTION for e in errors))
    
    def test_break_outside_loop(self):
        """Test: break statement outside loop"""
        code = "break"
        errors, _ = self._analyze(code)
        
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any(e.error_type == ErrorType.BREAK_OUTSIDE_LOOP for e in errors))
    
    def test_continue_outside_loop(self):
        """Test: continue statement outside loop"""
        code = "continue"
        errors, _ = self._analyze(code)
        
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any(e.error_type == ErrorType.CONTINUE_OUTSIDE_LOOP for e in errors))
    
    def test_break_inside_loop_ok(self):
        """Test: break statement inside loop (OK)"""
        code = """for i in range(10):
    break
"""
        errors, _ = self._analyze(code)
        # No break outside loop errors
        self.assertFalse(any(e.error_type == ErrorType.BREAK_OUTSIDE_LOOP for e in errors))
    
    def test_continue_inside_loop_ok(self):
        """Test: continue statement inside loop (OK)"""
        code = """while True:
    continue
"""
        errors, _ = self._analyze(code)
        # No continue outside loop errors
        self.assertFalse(any(e.error_type == ErrorType.CONTINUE_OUTSIDE_LOOP for e in errors))
    
    def test_division_by_zero(self):
        """Test: Division by zero constant"""
        code = "x = 42 / 0"
        errors, _ = self._analyze(code)
        
        self.assertTrue(any(e.error_type == ErrorType.CONST_DIVISION_BY_ZERO for e in errors))
    
    def test_redefinition_builtin_warning(self):
        """Test: Redefining built-in type (warning)"""
        code = "int = 5"
        errors, _ = self._analyze(code)
        
        # This should be detected but warnings are stored separately
        # Check in warnings or combined output
        total_warnings = len(self.analyzer.warnings)
        self.assertTrue(total_warnings > 0)
    
    def test_function_with_correct_args(self):
        """Test: Function call with correct number of arguments"""
        code = """def foo(a, b):
    return a + b

result = foo(1, 2)
"""
        errors, _ = self._analyze(code)
        # Should not have argument count mismatch errors
        self.assertFalse(any(e.error_type == ErrorType.ARGUMENT_COUNT_MISMATCH for e in errors))
    
    def test_return_inside_function_ok(self):
        """Test: return statement inside function (OK)"""
        code = """def foo():
    return 42
"""
        errors, _ = self._analyze(code)
        # Should not have return outside function errors
        self.assertFalse(any(e.error_type == ErrorType.RETURN_OUTSIDE_FUNCTION for e in errors))
    
    def test_variable_declaration_ok(self):
        """Test: Variable declaration and use (OK)"""
        code = """x = 5
y = x + 10
print(y)
"""
        errors, _ = self._analyze(code)
        # Should not have undeclared identifier errors
        self.assertFalse(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_nested_function_scopes(self):
        """Test: Nested function scopes"""
        code = """def outer():
    x = 5
    
    def inner():
        return x
    
    return inner()
"""
        errors, _ = self._analyze(code)
        # Should not have undeclared identifier errors for x in inner()
        self.assertFalse(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_for_loop_variable_ok(self):
        """Test: For loop variable declaration (OK)"""
        code = """for i in range(10):
    print(i)
"""
        errors, _ = self._analyze(code)
        # Should not have undeclared identifier errors for i
        self.assertFalse(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_function_parameter_ok(self):
        """Test: Function parameter declaration (OK)"""
        code = """def foo(a, b):
    return a + b
"""
        errors, _ = self._analyze(code)
        # Should not have undeclared identifier errors for a and b
        self.assertFalse(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_builtin_function_call_ok(self):
        """Test: Built-in function call (OK)"""
        code = """result = len([1, 2, 3])
print(result)
"""
        errors, _ = self._analyze(code)
        # Should not have undeclared identifier errors for len
        self.assertFalse(any(e.error_type == ErrorType.UNDECLARED_IDENTIFIER for e in errors))
    
    def test_multiple_errors(self):
        """Test: Multiple semantic errors"""
        code = """return 42
break
continue
"""
        errors, _ = self._analyze(code)
        
        # Should detect multiple errors
        self.assertTrue(len(errors) >= 3)
    
    def test_correct_code_no_errors(self):
        """Test: Correct code should have no semantic errors"""
        code = """def greet(name):
    greeting = "Hello, " + name
    return greeting

result = greet("World")
for i in range(3):
    print(i)
"""
        errors, _ = self._analyze(code)
        
        # Filter out only critical semantic errors (not warnings)
        critical_errors = [e for e in errors if e.error_type != ErrorType.REDEFINITION_BUILTIN]
        
        self.assertEqual(len(critical_errors), 0)


class TestSemanticErrorMessages(unittest.TestCase):
    """Тесты форматирования сообщений о ошибках"""
    
    def test_error_string_representation(self):
        """Test: Error string representation"""
        from semantic_analyzer.errors import SemanticError
        
        error = SemanticError(
            ErrorType.UNDECLARED_IDENTIFIER,
            "Name 'x' is not defined",
            5,
            10
        )
        
        error_str = str(error)
        self.assertIn("5:10", error_str)
        self.assertIn("UNDECLARED_IDENTIFIER", error_str)
        self.assertIn("Name 'x' is not defined", error_str)
    
    def test_error_repr(self):
        """Test: Error repr"""
        from semantic_analyzer.errors import SemanticError
        
        error = SemanticError(
            ErrorType.ARGUMENT_COUNT_MISMATCH,
            "Function 'foo' expects 2 arguments, got 1",
            10,
            5
        )
        
        repr_str = repr(error)
        self.assertIn("ARGUMENT_COUNT_MISMATCH", repr_str)
        self.assertIn("10", repr_str)
        self.assertIn("5", repr_str)


if __name__ == '__main__':
    unittest.main()
