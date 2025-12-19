    def parse_print(self) -> Print:
        """Разбор оператора print (Python 2)
        
        Синтаксис:
            print              - пустой print
            print expr         - один аргумент
            print expr1, expr2 - несколько аргументов через запятую
            print expr,        - с запятой в конце (без новой строки)
            
        Ошибки:
            print expr1 expr2  - ОШИБКА: нет запятой между выражениями
        """
        print_token = self.advance()  # print
        print_node = Print(line=print_token.line, column=print_token.column)
        
        # Если сразу конец строки/файла, это валидный пустой print
        if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            return print_node
        
        # Парсим первый аргумент
        first_arg = self.parse_expression()
        if not first_arg:
            # Некорректное выражение после print
            self.errors.append(
                f"Строка {print_token.line}:{print_token.column}: "
                f"Ожидается выражение после print"
            )
            return print_node
        
        print_node.args.append(first_arg)
        
        # Теперь парсим остальные аргументы, каждый должен быть отделён запятой
        while self.current_token().type == TokenType.COMMA:
            comma_token = self.current_token()
            self.advance()  # пропускаем запятую
            
            # Проверяем, есть ли аргумент после запятой
            if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
                # Запятая в конце: print(x,) - это означает без новой строки в Python2
                print_node.newline = False
                break
            
            # Парсим следующий аргумент
            arg = self.parse_expression()
            if not arg:
                self.errors.append(
                    f"Строка {comma_token.line}:{comma_token.column}: "
                    f"Ожидается выражение после запятой в операторе print"
                )
                break
            
            print_node.args.append(arg)
        
        # После всех аргументов должен быть конец строки/файла/блока или ошибка
        if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            self.errors.append(
                f"Строка {self.current_token().line}:{self.current_token().column}: "
                f"Неожиданный токен '{self.current_token().value}' в операторе print. "
                f"Аргументы должны быть разделены запятыми."
            )
        
        return print_node
