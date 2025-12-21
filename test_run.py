#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ныбыстрый тест семантического анализатора
"""

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from semantic_analyzer.errors import ErrorType


def test_error(name, code, expected_error_type):
    """Тестировать одну ошибку"""
    print(f"\n{'='*60}")
    print(f"ОШИБКА: {name}")
    print(f"{'='*60}")
    print(f"Код:\n{code}")
    print("-" * 60)
    
    try:
        lexer = Lexer(code)
        tokens = lexer.scan()
        
        if lexer.errors:
            print("❌ Лексические ошибки:")
            for error in lexer.errors:
                print(f"  {error}")
            return
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            print("❌ Синтаксические ошибки:")
            for error in parser.errors:
                print(f"  {error}")
            return
        
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        if errors:
            found = False
            for error in errors:
                print(f"\n✅ Найдена ошибка:")
                print(f"   Тип: {error.error_type.name}")
                print(f"   Описание: {error.message}")
                print(f"   Локация: строка {error.line}, столбец {error.column}")
                
                if error.error_type == expected_error_type:
                    found = True
            
            if found:
                print(f"\n✅ ПРОВЕРКА ПРОЙДЕНА: Найдена ожидаемая ошибка")
            else:
                print(f"\n❌ ПРОВЕРКА НЕ ПРОйДЕНА: Ожидался {expected_error_type.name}")
        else:
            print("❌ Ошибки не обнаружены")
    
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТОВАНИИ: {str(e)}")
        import traceback
        traceback.print_exc()


def test_correct_code(name, code):
    """Тестировать корректный код"""
    print(f"\n{'='*60}")
    print(f"КОРРЕКТНЫЙ КОД: {name}")
    print(f"{'='*60}")
    print(f"Код:\n{code}")
    print("-" * 60)
    
    try:
        lexer = Lexer(code)
        tokens = lexer.scan()
        
        if lexer.errors:
            print("❌ Лексические ошибки")
            return
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            print("❌ Синтаксические ошибки")
            return
        
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        # Фильтруем варнинги
        critical_errors = [e for e in errors if e.error_type != ErrorType.REDEFINITION_BUILTIN]
        
        if critical_errors:
            print("❌ Найдены ошибки:")
            for error in critical_errors:
                print(f"  {error}")
        else:
            print("✅ ПРОВЕРКА ПРОЙДЕНА: без критических ошибок")
    
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТОВАНИИ: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    print("\n" + "#" * 60)
    print("# ТЕСТОВАНИЕ СЕМАНТИЧЕСКОГО АНАЛИЗАТОРА")
    print("#" * 60)
    
    # 1. UndeclaredIdentifier
    test_error(
        "UndeclaredIdentifier",
        "print(undefined_var)",
        ErrorType.UNDECLARED_IDENTIFIER
    )
    
    # 2. ArgumentCountMismatch
    test_error(
        "ArgumentCountMismatch",
        """def foo(a, b):
    pass

foo(1)""",
        ErrorType.ARGUMENT_COUNT_MISMATCH
    )
    
    # 3. ReturnOutsideFunction
    test_error(
        "ReturnOutsideFunction",
        "return 42",
        ErrorType.RETURN_OUTSIDE_FUNCTION
    )
    
    # 4. BreakOutsideLoop
    test_error(
        "BreakOutsideLoop",
        "break",
        ErrorType.BREAK_OUTSIDE_LOOP
    )
    
    # 5. ContinueOutsideLoop
    test_error(
        "ContinueOutsideLoop",
        "continue",
        ErrorType.CONTINUE_OUTSIDE_LOOP
    )
    
    # 6. ConstDivisionByZero
    test_error(
        "ConstDivisionByZero",
        "x = 42 / 0",
        ErrorType.CONST_DIVISION_BY_ZERO
    )
    
    # 7. Break inside loop - OK
    test_correct_code(
        "Break inside loop",
        """for i in range(10):
    break"""
    )
    
    # 8. Return inside function - OK
    test_correct_code(
        "Return inside function",
        """def foo():
    return 42"""
    )
    
    # 9. Variable declaration and use - OK
    test_correct_code(
        "Variable declaration and use",
        """x = 5
y = x + 10
print(y)"""
    )
    
    # 10. Function with correct args - OK
    test_correct_code(
        "Function with correct arguments",
        """def foo(a, b):
    return a + b

result = foo(1, 2)"""
    )
    
    print(f"\n\n{'#' * 60}")
    print("# ТЕСТОВАНИЕ ЗАВЕРШЕНО")
    print("#" * 60 + "\n")


if __name__ == '__main__':
    main()
