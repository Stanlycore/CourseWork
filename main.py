        # 2. Синтаксический анализ
        self.logger.section("ЭТАП 2: СИНТАКСИЧЕСКИЙ АНАЛИЗ")
        self._log("\n[2/5] Синтаксический анализ...")
        
        try:
            self.logger.info("Создание парсера...")
            self.parser = Parser(tokens)
            self.logger.info("Парсер создан успешно")
            
            self.logger.info("Запуск парсинга...")
            self.ast = self.parser.parse()
            self.logger.info(f"Парсинг завершен. Тип корневого узла: {type(self.ast).__name__}")
            
            if self.parser.errors:
                self.logger.error(f"Обнаружено синтаксических ошибок: {len(self.parser.errors)}")
                for i, error in enumerate(self.parser.errors, 1):
                    self.logger.error(f"  Ошибка {i}: {error}")
                
                self._log("\n✘ Обнаружены синтаксические ошибки:", 'error')
                for error in self.parser.errors:
                    self._log(f"  • {error}", 'error')
                return
            
            self.logger.info("Синтаксический анализ завершен успешно")
            self._log("✔ Синтаксическое дерево построено", 'success')
            
            # Преобразование AST в структурированное дерево
            self.logger.info("Преобразование AST в структурированное дерево...")
            tree_node = self.tree_visitor.visit(self.ast)
            self.logger.info("Дерево преобразовано успешно")
            
            # Отображение дерева
            self.logger.info("Отображение текстового дерева...")
            self._display_tree_text(tree_node)
            self.logger.info("Текстовое дерево отображено")
            
            self.logger.info("Отображение графического дерева...")
            self._display_tree_graph(tree_node)
            self.logger.info("Графическое дерево отображено")
            
        except Exception as e:
            self.logger.exception(f"Ошибка при синтаксическом анализе: {str(e)}")
            raise
