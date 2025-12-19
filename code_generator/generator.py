    def generate_print(self, node: Print) -> str:
        """Генерирование print → print() в Python 3
        
        Тек как парсер теперь строгий и проверяет синтаксис,
        тут мы можем его просто генерировать.
        """
        args = [self.generate_expression(arg) for arg in node.args]
        
        params = ', '.join(args)
        if params:
            code = f"{self.indent()}print({params}"
        else:
            code = f"{self.indent()}print("
        
        if not node.newline:
            code += ", end='')"
        else:
            code += ")"
        
        code += "\n"
        return code
