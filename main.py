#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Транслятор Python2 → Python3
Курсовая работа по ТЯП
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, List

from lexer import Lexer, Token, TokenType
from parser import Parser
from parser.ast_nodes import ASTNode, Program
from identifier_table import IdentifierTable
from optimizer import Optimizer
from code_generator import CodeGenerator
from examples.examples import EXAMPLES


class TranslatorGUI:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Транслятор Python2 → Python3")
        self.root.geometry("1600x900")
        
        # Компоненты
        self.lexer: Optional[Lexer] = None
        self.parser: Optional[Parser] = None
        self.id_table: Optional[IdentifierTable] = None
        self.optimizer = Optimizer()
        self.generator = CodeGenerator()
        self.ast: Optional[ASTNode] = None
        
        # Цвета для scope
        self.scope_colors = [
            '#E8F5E9', '#FFF9C4', '#FFE0B2', '#FFCCBC', '#FFAB91',
            '#F8BBD0', '#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB',
            '#B3E5FC', '#B2EBF2', '#B2DFDB', '#C8E6C9', '#DCEDC8'
        ]
        
        self._setup_ui()
        self._setup_styles()
        self._load_first_example()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Главный notebook
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка основного интерфейса
        self.main_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.main_tab, text="Транслятор")
        
        # Вкладка анализа
        self.analysis_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.analysis_tab, text="Анализ")
        
        self._setup_main_tab()
        self._setup_analysis_tab()
    
    def _setup_main_tab(self):
        """Настройка основной вкладки"""
        # Горизонтальный разделитель
        main_paned = ttk.PanedWindow(self.main_tab, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая часть - ввод
        left_frame = ttk.LabelFrame(main_paned, text="Python 2 код", padding=10)
        main_paned.add(left_frame, weight=1)
        
        # Панель примеров
        example_frame = ttk.Frame(left_frame)
        example_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(example_frame, text="Пример:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.example_var = tk.StringVar()
        self.example_combo = ttk.Combobox(
            example_frame,
            textvariable=self.example_var,
            values=list(EXAMPLES.keys()),
            state='readonly',
            width=40
        )
        self.example_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.example_combo.bind('<<ComboboxSelected>>', self._on_example_selected)
        
        # Поле ввода
        self.input_text = scrolledtext.ScrolledText(
            left_frame, width=50, height=25, wrap=tk.WORD,
            font=('Courier New', 11)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопка анализа
        self.analyze_btn = ttk.Button(
            left_frame, text="▶ Анализировать и перевести",
            command=self._analyze, style='Accent.TButton'
        )
        self.analyze_btn.pack(fill=tk.X, pady=5)
        
        # Правая часть - вывод
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)
        
        # Поле вывода Python 3
        output_frame = ttk.LabelFrame(right_paned, text="Python 3 код", padding=10)
        right_paned.add(output_frame, weight=3)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, width=50, height=15, wrap=tk.WORD,
            font=('Courier New', 11), state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Консоль ошибок
        console_frame = ttk.LabelFrame(right_paned, text="Консоль", padding=10)
        right_paned.add(console_frame, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame, height=8, wrap=tk.WORD,
            font=('Courier New', 10), state=tk.DISABLED
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_analysis_tab(self):
        """Настройка вкладки анализа"""
        # Notebook для подвкладок
        analysis_notebook = ttk.Notebook(self.analysis_tab)
        analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка синтаксического дерева
        tree_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(tree_frame, text="Синтаксическое дерево")
        
        self.tree_text = scrolledtext.ScrolledText(
            tree_frame, wrap=tk.WORD, font=('Courier New', 10)
        )
        self.tree_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка таблицы лексем
        tokens_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(tokens_frame, text="Таблица лексем")
        
        tokens_columns = ('line', 'col', 'type', 'value')
        self.tokens_tree = ttk.Treeview(
            tokens_frame, columns=tokens_columns, show='headings', height=20
        )
        
        self.tokens_tree.heading('line', text='Строка')
        self.tokens_tree.heading('col', text='Столбец')
        self.tokens_tree.heading('type', text='Тип')
        self.tokens_tree.heading('value', text='Значение')
        
        self.tokens_tree.column('line', width=70, anchor='center')
        self.tokens_tree.column('col', width=70, anchor='center')
        self.tokens_tree.column('type', width=150, anchor='w')
        self.tokens_tree.column('value', width=300, anchor='w')
        
        tokens_scroll = ttk.Scrollbar(
            tokens_frame, orient=tk.VERTICAL, command=self.tokens_tree.yview
        )
        self.tokens_tree.configure(yscrollcommand=tokens_scroll.set)
        
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tokens_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Вкладка таблицы идентификаторов
        id_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(id_frame, text="Таблица идентификаторов")
        
        id_columns = ('name', 'scope', 'kind', 'type', 'value', 'address')
        self.id_tree = ttk.Treeview(
            id_frame, columns=id_columns, show='headings', height=20
        )
        
        self.id_tree.heading('name', text='Имя')
        self.id_tree.heading('scope', text='Область')
        self.id_tree.heading('kind', text='Вид')
        self.id_tree.heading('type', text='Тип')
        self.id_tree.heading('value', text='Значение')
        self.id_tree.heading('address', text='Адрес')
        
        self.id_tree.column('name', width=120, anchor='w')
        self.id_tree.column('scope', width=70, anchor='center')
        self.id_tree.column('kind', width=80, anchor='center')
        self.id_tree.column('type', width=80, anchor='center')
        self.id_tree.column('value', width=120, anchor='w')
        self.id_tree.column('address', width=100, anchor='center')
        
        id_scroll = ttk.Scrollbar(
            id_frame, orient=tk.VERTICAL, command=self.id_tree.yview
        )
        self.id_tree.configure(yscrollcommand=id_scroll.set)
        
        self.id_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        id_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        
        style.configure('Accent.TButton', font=('Arial', 11, 'bold'))
        
        # Цветовые теги для токенов
        self.tokens_tree.tag_configure('keyword', background='#E3F2FD')
        self.tokens_tree.tag_configure('identifier', background='#F1F8E9')
        self.tokens_tree.tag_configure('number', background='#FFF3E0')
        self.tokens_tree.tag_configure('string', background='#FCE4EC')
        self.tokens_tree.tag_configure('error', background='#FFEBEE')
        
        # Теги для консоли
        self.console_text.tag_configure('error', foreground='#D32F2F', font=('Courier New', 10, 'bold'))
        self.console_text.tag_configure('success', foreground='#388E3C', font=('Courier New', 10, 'bold'))
        self.console_text.tag_configure('warning', foreground='#F57C00', font=('Courier New', 10, 'bold'))
    
    def _load_first_example(self):
        """Загрузить первый пример"""
        if EXAMPLES:
            first = list(EXAMPLES.keys())[0]
            self.example_var.set(first)
            self._on_example_selected(None)
    
    def _on_example_selected(self, event):
        """Обработчик выбора примера"""
        name = self.example_var.get()
        if name in EXAMPLES:
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', EXAMPLES[name])
    
    def _clear_views(self):
        """Очистить все поля вывода"""
        # Очистка таблицы токенов
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        
        # Очистка таблицы идентификаторов
        for item in self.id_tree.get_children():
            self.id_tree.delete(item)
        
        # Очистка консоли
        self.console_text.configure(state=tk.NORMAL)
        self.console_text.delete('1.0', tk.END)
        self.console_text.configure(state=tk.DISABLED)
        
        # Очистка вывода
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state=tk.DISABLED)
        
        # Очистка дерева
        self.tree_text.delete('1.0', tk.END)
    
    def _log(self, message: str, tag: str = None):
        """Вывести сообщение в консоль"""
        self.console_text.configure(state=tk.NORMAL)
        if tag:
            self.console_text.insert(tk.END, message + "\n", tag)
        else:
            self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.console_text.configure(state=tk.DISABLED)
    
    def _analyze(self):
        """Главная функция анализа"""
        self._clear_views()
        
        source = self.input_text.get('1.0', tk.END)
        
        self._log("=" * 60)
        self._log("НАЧАЛО АНАЛИЗА", 'success')
        self._log("=" * 60)
        
        # 1. Лексический анализ
        self._log("\n[1/5] Лексический анализ...")
        self.lexer = Lexer(source)
        self.id_table = self.lexer.identifier_table
        
        tokens = self.lexer.scan()
        
        if self.lexer.errors:
            self._log("\n✘ Обнаружены лексические ошибки:", 'error')
            for error in self.lexer.errors:
                self._log(f"  • {error}", 'error')
            return
        
        self._log(f"✔ Найдено {len(tokens)} токенов", 'success')
        
        # Заполнение таблицы токенов
        self._fill_tokens_table(tokens)
        self._fill_identifier_table()
        
        # 2. Синтаксический анализ
        self._log("\n[2/5] Синтаксический анализ...")
        self.parser = Parser(tokens)
        self.ast = self.parser.parse()
        
        if self.parser.errors:
            self._log("\n✘ Обнаружены синтаксические ошибки:", 'error')
            for error in self.parser.errors:
                self._log(f"  • {error}", 'error')
            return
        
        self._log("✔ Синтаксическое дерево построено", 'success')
        
        # Отображение дерева
        self._display_ast(self.ast)
        
        # 3. Оптимизация
        self._log("\n[3/5] Оптимизация...")
        optimized_ast = self.optimizer.optimize(self.ast)
        self._log(f"✔ Применено {self.optimizer.optimizations_applied} оптимизаций", 'success')
        
        # 4. Генерация кода
        self._log("\n[4/5] Генерация Python 3 кода...")
        python3_code = self.generator.generate(optimized_ast)
        
        # Вывод результата
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert('1.0', python3_code)
        self.output_text.configure(state=tk.DISABLED)
        
        self._log("✔ Код успешно сгенерирован", 'success')
        
        # 5. Завершение
        self._log("\n" + "=" * 60)
        self._log("АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!", 'success')
        self._log("=" * 60)
    
    def _fill_tokens_table(self, tokens: List[Token]):
        """Заполнить таблицу токенов"""
        for token in tokens:
            if token.type == TokenType.EOF:
                continue
            
            tag = ''
            if 'KEYWORD' in token.type.name or token.type.name in ('PRINT', 'DEF', 'CLASS', 'IF', 'WHILE', 'FOR'):
                tag = 'keyword'
            elif token.type == TokenType.IDENTIFIER:
                tag = 'identifier'
            elif token.type == TokenType.NUMBER:
                tag = 'number'
            elif token.type == TokenType.STRING:
                tag = 'string'
            elif token.type == TokenType.UNKNOWN:
                tag = 'error'
            
            self.tokens_tree.insert(
                '', tk.END,
                values=(token.line, token.column, token.type.name, str(token.value)),
                tags=(tag,)
            )
    
    def _fill_identifier_table(self):
        """Заполнить таблицу идентификаторов"""
        if not self.id_table:
            return
        
        # Настройка цветов для scope
        self._configure_scope_tags()
        
        for entry in self.id_table.get_all_entries():
            value_str = str(entry.value) if entry.value else "-"
            addr_str = f"({entry.bucket},{entry.pos})"
            scope_tag = f'scope_{entry.scope}'
            
            self.id_tree.insert(
                '', tk.END,
                values=(entry.name, entry.scope, entry.kind, entry.type_, value_str, addr_str),
                tags=(scope_tag,)
            )
    
    def _configure_scope_tags(self):
        """Настройка цветов для областей видимости"""
        if not self.id_table:
            return
        
        scopes = self.id_table.get_all_scopes()
        for scope in scopes:
            tag_name = f'scope_{scope}'
            color = self._get_scope_color(scope)
            self.id_tree.tag_configure(tag_name, background=color)
    
    def _get_scope_color(self, scope: str) -> str:
        """Получить цвет для области видимости"""
        hash_val = sum(ord(c) for c in scope)
        return self.scope_colors[hash_val % len(self.scope_colors)]
    
    def _display_ast(self, node: ASTNode, level: int = 0):
        """Отобразить AST в текстовом виде"""
        indent = "  " * level
        node_type = type(node).__name__
        
        # Добавление информации о узле
        if hasattr(node, 'name') and node.name:
            self.tree_text.insert(tk.END, f"{indent}{node_type}(name='{node.name}')\n")
        elif hasattr(node, 'id') and node.id:
            self.tree_text.insert(tk.END, f"{indent}{node_type}(id='{node.id}')\n")
        elif hasattr(node, 'value') and node.value is not None:
            self.tree_text.insert(tk.END, f"{indent}{node_type}(value={repr(node.value)})\n")
        elif hasattr(node, 'op') and node.op:
            self.tree_text.insert(tk.END, f"{indent}{node_type}(op='{node.op}')\n")
        else:
            self.tree_text.insert(tk.END, f"{indent}{node_type}\n")
        
        # Рекурсия по дочерним узлам
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                self._display_ast(child, level + 1)
        
        if hasattr(node, 'condition') and node.condition:
            self._display_ast(node.condition, level + 1)
        
        if hasattr(node, 'then_body') and node.then_body:
            for child in node.then_body:
                self._display_ast(child, level + 1)
        
        if hasattr(node, 'else_body') and node.else_body:
            for child in node.else_body:
                self._display_ast(child, level + 1)
        
        if hasattr(node, 'left') and node.left:
            self._display_ast(node.left, level + 1)
        
        if hasattr(node, 'right') and node.right:
            self._display_ast(node.right, level + 1)
        
        if hasattr(node, 'operand') and node.operand:
            self._display_ast(node.operand, level + 1)
        
        if hasattr(node, 'target') and node.target:
            self._display_ast(node.target, level + 1)
        
        if hasattr(node, 'value') and isinstance(node.value, ASTNode):
            self._display_ast(node.value, level + 1)
        
        if hasattr(node, 'args') and node.args:
            for arg in node.args:
                if isinstance(arg, ASTNode):
                    self._display_ast(arg, level + 1)


def main():
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
