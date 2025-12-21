#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Транслятор Python2 → Python3
Курсовая работа по ТЯП
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, List, Tuple
import traceback
import sys

from lexer import Lexer, Token, TokenType
from parser import Parser, ASTToTreeVisitor, TreeNode
from parser.ast_nodes import ASTNode, Program
from identifier_table import IdentifierTable
from semantic_analyzer import SemanticAnalyzer
from optimizer import Optimizer
from code_generator import CodeGenerator
from examples.examples import EXAMPLES
from logger import TranslatorLogger


class ASTVisualizer:
    """Визуализатор синтаксического дерева на Canvas"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_width = 140
        self.node_height = 50
        self.level_height = 100
        self.horizontal_spacing = 30
        self.node_positions = {}  # {node_id: (x, y)}
        self.next_x = 50  # Следующая X координата
        self.tree_root: Optional[TreeNode] = None
        
    def clear(self):
        """Очистить canvas"""
        self.canvas.delete('all')
        self.node_positions = {}
        self.next_x = 50
        self.tree_root = None
    
    def draw_tree(self, tree_node: TreeNode):
        """Нарисовать дерево на основе TreeNode"""
        self.clear()
        if not tree_node:
            return
        
        self.tree_root = tree_node
        
        # Рассчитываем позиции узлов
        self._calculate_positions(tree_node, 0)
        
        # Рисуем соединения
        self._draw_connections(tree_node)
        
        # Рисуем узлы
        self._draw_nodes(tree_node)
        
        # Обновляем регион прокрутки
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _calculate_positions(self, node: TreeNode, level: int) -> Tuple[int, int]:
        """Рассчитать позиции узлов"""
        if not node:
            return (0, 0)
        
        node_id = id(node)
        y = 50 + level * self.level_height
        
        children = node.children
        
        if not children:
            # Листовой узел
            x = self.next_x
            self.next_x += self.node_width + self.horizontal_spacing
            self.node_positions[node_id] = (x, y)
            return (x, y)
        
        # Рассчитываем позиции детей
        child_positions = []
        for child in children:
            if child:
                pos = self._calculate_positions(child, level + 1)
                child_positions.append(pos)
        
        if child_positions:
            # Позиция родителя - центр между детьми
            min_x = min(pos[0] for pos in child_positions)
            max_x = max(pos[0] for pos in child_positions)
            x = (min_x + max_x) // 2
        else:
            x = self.next_x
            self.next_x += self.node_width + self.horizontal_spacing
        
        self.node_positions[node_id] = (x, y)
        return (x, y)
    
    def _draw_connections(self, node: TreeNode):
        """Нарисовать соединения между узлами"""
        if not node:
            return
        
        node_id = id(node)
        if node_id not in self.node_positions:
            return
        
        x1, y1 = self.node_positions[node_id]
        
        for child in node.children:
            if child:
                child_id = id(child)
                if child_id in self.node_positions:
                    x2, y2 = self.node_positions[child_id]
                    # Линия от центра родителя к центру ребенка
                    self.canvas.create_line(
                        x1 + self.node_width // 2, y1 + self.node_height,
                        x2 + self.node_width // 2, y2,
                        fill='#666666', width=2, arrow=tk.LAST
                    )
                    self._draw_connections(child)
    
    def _draw_nodes(self, node: TreeNode):
        """Нарисовать узлы"""
        if not node:
            return
        
        node_id = id(node)
        if node_id not in self.node_positions:
            return
        
        x, y = self.node_positions[node_id]
        
        # Определяем текст и цвет узла
        node_color = self._get_node_color(node.node_type)
        
        node_text = node.name
        if node.value:
            node_text = f"{node.name}\n{node.value}"
        
        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
            x, y, x + self.node_width, y + self.node_height,
            fill=node_color, outline='#333333', width=2
        )
        
        # Рисуем текст
        text = self.canvas.create_text(
            x + self.node_width // 2, y + self.node_height // 2,
            text=node_text, font=('Arial', 9, 'bold'),
            fill='#000000', width=self.node_width - 10
        )
        
        # Рекурсивно рисуем детей
        for child in node.children:
            if child:
                self._draw_nodes(child)
    
    def _get_node_color(self, node_type: str) -> str:
        """Получить цвет узла по типу"""
        color_map = {
            'keyword': '#FFE082',
            'operator': '#FFB74D',
            'operand': '#CE93D8',
            'condition': '#B3E5FC',
            'body': '#C5E1A5',
            'default': '#E0E0E0',
        }
        return color_map.get(node_type, '#E0E0E0')


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
        self.semantic_analyzer = SemanticAnalyzer()
        self.optimizer = Optimizer()
        self.generator = CodeGenerator()
        self.ast: Optional[ASTNode] = None
        self.ast_visualizer: Optional[ASTVisualizer] = None
        self.tree_visitor = ASTToTreeVisitor()
        
        # Логгер
        self.logger = TranslatorLogger()
        
        # Цвета для scope
        self.scope_colors = [
            '#E8F5E9', '#FFF9C4', '#FFE0B2', '#FFCCBC', '#FFAB91',
            '#F8BBD0', '#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB',
            '#B3E5FC', '#B2EBF2', '#B2DFDB', '#C8E6C9', '#DCEDC8'
        ]
        
        self._setup_ui()
        self._setup_styles()
        self._setup_shortcuts()
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
        
        # Поле ввода (укрупненный шрифт)
        self.input_text = scrolledtext.ScrolledText(
            left_frame, width=50, height=25, wrap=tk.WORD,
            font=('Courier New', 14)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопка анализа
        self.analyze_btn = ttk.Button(
            left_frame, text="▶ Анализировать и перевести",
            command=self._analyze_safe, style='Accent.TButton'
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
            font=('Courier New', 14), state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Панель кнопок под выводом
        output_buttons = ttk.Frame(output_frame)
        output_buttons.pack(fill=tk.X, pady=(5, 0))
        
        self.copy_output_btn = ttk.Button(
            output_buttons,
            text="Копировать в буфер обмена",
            command=self._copy_output_to_clipboard
        )
        self.copy_output_btn.pack(side=tk.RIGHT)
        
        # Консоль ошибок
        console_frame = ttk.LabelFrame(right_paned, text="Консоль", padding=10)
        right_paned.add(console_frame, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame, height=8, wrap=tk.WORD,
            font=('Courier New', 12), state=tk.DISABLED
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_analysis_tab(self):
        """Настройка вкладки анализа"""
        # Notebook для подвкладок
        analysis_notebook = ttk.Notebook(self.analysis_tab)
        analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка синтаксического дерева (ГРАФИКА)
        tree_graph_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(tree_graph_frame, text="🌲 Дерево (графика)")
        
        # Canvas с прокруткою
        canvas_frame = ttk.Frame(tree_graph_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем canvas и scrollbars
        self.tree_canvas = tk.Canvas(
            canvas_frame, bg='white', width=800, height=600
        )
        
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.tree_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.tree_canvas.yview)
        
        self.tree_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Размещаем элементы
        self.tree_canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Создаем визуализатор
        self.ast_visualizer = ASTVisualizer(self.tree_canvas)
        
        # Вкладка синтаксического дерева (ТЕКСТ)
        tree_text_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(tree_text_frame, text="📄 Дерево (текст)")
        
        self.tree_text = scrolledtext.ScrolledText(
            tree_text_frame, wrap=tk.WORD, font=('Courier New', 12)
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
        
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
        # Цветовые теги для токенов
        self.tokens_tree.tag_configure('keyword', background='#E3F2FD')
        self.tokens_tree.tag_configure('identifier', background='#F1F8E9')
        self.tokens_tree.tag_configure('number', background='#FFF3E0')
        self.tokens_tree.tag_configure('string', background='#FCE4EC')
        self.tokens_tree.tag_configure('error', background='#FFEBEE')
        
        # Теги для консоли
        self.console_text.tag_configure('error', foreground='#D32F2F', font=('Courier New', 12, 'bold'))
        self.console_text.tag_configure('success', foreground='#388E3C', font=('Courier New', 12, 'bold'))
        self.console_text.tag_configure('warning', foreground='#F57C00', font=('Courier New', 12, 'bold'))
    
    def _setup_shortcuts(self):
        """Горячие клавиши для полей ввода/вывода"""
        for widget in (self.input_text, self.output_text, self.console_text, self.tree_text):
            widget.bind('<Control-a>', self._select_all)
            widget.bind('<Control-A>', self._select_all)
            widget.bind('<Control-c>', self._copy)
            widget.bind('<Control-C>', self._copy)
            widget.bind('<Control-v>', self._paste)
            widget.bind('<Control-V>', self._paste)
    
    def _select_all(self, event):
        widget = event.widget
        widget.tag_add('sel', '1.0', 'end-1c')
        return 'break'
    
    def _copy(self, event):
        widget = event.widget
        try:
            text = widget.get('sel.first', 'sel.last')
        except tk.TclError:
            return 'break'
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        return 'break'
    
    def _paste(self, event):
        widget = event.widget
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            return 'break'
        widget.insert('insert', text)
        return 'break'
    
    def _copy_output_to_clipboard(self):
        """Скопировать Python 3 код в буфер обмена"""
        self.output_text.configure(state=tk.NORMAL)
        text = self.output_text.get('1.0', 'end-1c')
        self.output_text.configure(state=tk.DISABLED)
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self._log("✔ Код скопирован в буфер обмена", 'success')
        else:
            self._log("⚠ Нет кода для копирования", 'warning')
    
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
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        
        for item in self.id_tree.get_children():
            self.id_tree.delete(item)
        
        self.console_text.configure(state=tk.NORMAL)
        self.console_text.delete('1.0', tk.END)
        self.console_text.configure(state=tk.DISABLED)
        
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state=tk.DISABLED)
        
        self.tree_text.delete('1.0', tk.END)
        
        if self.ast_visualizer:
            self.ast_visualizer.clear()
    
    def _log(self, message: str, tag: str = None):
        """Вывести сообщение в консоль"""
        self.console_text.configure(state=tk.NORMAL)
        if tag:
            self.console_text.insert(tk.END, message + "\n", tag)
        else:
            self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.console_text.configure(state=tk.DISABLED)
    
    def _analyze_safe(self):
        """Безопасный вызов анализа с обработкой исключений"""
        try:
            log_file = self.logger.start_new_session()
            self.logger.info(f"Python версия: {sys.version}")
            self.logger.info(f"Tkinter версия: {tk.TkVersion}")
            
            self._analyze()
            
            self.logger.close()
            
        except Exception as e:
            self.logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            self.logger.exception("Traceback:")
            self.logger.close()
            
            error_msg = f"Произошла критическая ошибка:\n{str(e)}\n\nЛог сохранен в: {self.logger.current_log_file}"
            self._log(f"\n✘ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}", 'error')
            messagebox.showerror("Ошибка", error_msg)
    
    def _analyze(self):
        """Главная функция анализа"""
        self.logger.section("НАЧАЛО АНАЛИЗА")
        self._clear_views()
        
        source = self.input_text.get('1.0', tk.END)
        self.logger.info(f"Длина исходного кода: {len(source)} символов")
        self.logger.debug(f"Первые 100 символов: {source[:100]}")
        
        self._log("=" * 60)
        self._log("✔ НАЧАЛО АНАЛИЗА", 'success')
        self._log("=" * 60)
        
        # 1. Лексический анализ
        self.logger.section("ЭТАП 1: ЛЕКСИЧЕСКИЙ АНАЛИЗ")
        self._log("\n[1/5] Лексический анализ...")
        
        try:
            self.logger.info("Создание лексера...")
            self.lexer = Lexer(source)
            self.logger.info("Лексер создан успешно")
            
            self.id_table = self.lexer.identifier_table
            self.logger.info("Таблица идентификаторов получена")
            
            self.logger.info("Запуск сканирования...")
            tokens = self.lexer.scan()
            self.logger.info(f"Сканирование завершено. Найдено токенов: {len(tokens)}")
            
            if self.lexer.errors:
                self.logger.error(f"Обнаружено лексических ошибок: {len(self.lexer.errors)}")
                for i, error in enumerate(self.lexer.errors, 1):
                    self.logger.error(f"  Ошибка {i}: {error}")
                
                self._log("\n✘ Обнаружены лексические ошибки:", 'error')
                for error in self.lexer.errors:
                    self._log(f"  {error}", 'error')
                return
            
            self.logger.info("Лексический анализ завершен успешно")
            self._log(f"✔ Найдено {len(tokens)} токенов", 'success')
            
            self.logger.info("Заполнение таблицы токенов...")
            self._fill_tokens_table(tokens)
            self.logger.info("Таблица токенов заполнена")
            
            self.logger.info("Заполнение таблицы идентификаторов...")
            self._fill_identifier_table()
            self.logger.info("Таблица идентификаторов заполнена")
            
        except Exception as e:
            self.logger.exception(f"Ошибка при лексическом анализе: {str(e)}")
            raise
        
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
                    self._log(f"  {error}", 'error')
                return
            
            self.logger.info("Синтаксический анализ завершен успешно")
            self._log("✔ Синтаксическое дерево построено", 'success')
            
            self.logger.info("Преобразование AST в структурированное дерево...")
            tree_node = self.tree_visitor.visit(self.ast)
            self.logger.info("Дерево преобразовано успешно")
            
            self.logger.info("Отображение текстового дерева...")
            self._display_tree_text(tree_node)
            self.logger.info("Текстовое дерево отображено")
            
            self.logger.info("Отображение графического дерева...")
            self._display_tree_graph(tree_node)
            self.logger.info("Графическое дерево отображено")
            
        except Exception as e:
            self.logger.exception(f"Ошибка при синтаксическом анализе: {str(e)}")
            raise
        
        # 3. Семантический анализ
        self.logger.section("ЭТАП 3: СЕМАНТИЧЕСКИЙ АНАЛИЗ")
        self._log("\n[3/5] Семантический анализ...")
        
        try:
            self.logger.info("Запуск семантического анализатора...")
            semantic_errors = self.semantic_analyzer.analyze(self.ast)
            self.logger.info(f"Семантический анализ завершен. Обнаружено ошибок: {len(semantic_errors)}")
            
            if semantic_errors:
                self.logger.error(f"Обнаружено семантических ошибок: {len(semantic_errors)}")
                for i, error in enumerate(semantic_errors, 1):
                    self.logger.error(f"  Ошибка {i}: {error}")
                
                self._log(f"\n✘ Обнаружены семантические ошибки ({len(semantic_errors)}):", 'error')
                for error in semantic_errors:
                    self._log(f"  {error}", 'error')
                return
            
            self.logger.info("Семантический анализ пройден успешно")
            self._log("✔ Семантический анализ пройден успешно", 'success')
            
        except Exception as e:
            self.logger.exception(f"Ошибка при семантическом анализе: {str(e)}")
            raise
        
        # 4. Оптимизация
        self.logger.section("ЭТАП 4: ОПТИМИЗАЦИЯ")
        self._log("\n[4/5] Оптимизация...")
        
        try:
            self.logger.info("Запуск оптимизатора...")
            optimized_ast = self.optimizer.optimize(self.ast)
            self.logger.info(f"Оптимизация завершена. Применено оптимизаций: {self.optimizer.optimizations_applied}")
            
            self._log(f"✔ Применено {self.optimizer.optimizations_applied} оптимизаций", 'success')
        except Exception as e:
            self.logger.exception(f"Ошибка при оптимизации: {str(e)}")
            raise
        
        # 5. Генерация кода
        self.logger.section("ЭТАП 5: ГЕНЕРАЦИЯ КОДА")
        self._log("\n[5/5] Генерация Python 3 кода...")
        
        try:
            self.logger.info("Запуск генератора кода...")
            python3_code = self.generator.generate(optimized_ast)
            self.logger.info(f"Генерация завершена. Длина кода: {len(python3_code)} символов")
            self.logger.debug(f"Первые 100 символов: {python3_code[:100]}")
            
            self.logger.info("Вывод результата в GUI...")
            self.output_text.configure(state=tk.NORMAL)
            self.output_text.insert('1.0', python3_code)
            self.output_text.configure(state=tk.DISABLED)
            self.logger.info("Результат выведен")
            
            self._log("✔ Код успешно сгенерирован", 'success')
            
        except Exception as e:
            self.logger.exception(f"Ошибка при генерации кода: {str(e)}")
            raise
        
        # 6. Завершение
        self.logger.section("ЗАВЕРШЕНИЕ")
        self.logger.info("Все этапы завершены успешно")
        
        self._log("\n" + "=" * 60)
        self._log("✔ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!", 'success')
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
    
    def _display_tree_text(self, tree_node: TreeNode, level: int = 0):
        """Отобразить дерево в текстовом виде"""
        if not tree_node:
            return
        
        indent = "  " * level
        
        if tree_node.value:
            self.tree_text.insert(tk.END, f"{indent}{tree_node.name} '{tree_node.value}'\n")
        else:
            self.tree_text.insert(tk.END, f"{indent}{tree_node.name}\n")
        
        for child in tree_node.children:
            self._display_tree_text(child, level + 1)
    
    def _display_tree_graph(self, tree_node: TreeNode):
        """Отобразить дерево графически"""
        if self.ast_visualizer and tree_node:
            self.ast_visualizer.draw_tree(tree_node)


def main():
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
