#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Таблица идентификаторов с поддержкой областей видимости
ИСПРАВЛЕННА ВЕРСИЯ: улучшена работа с вложенными областями
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class IdentifierEntry:
    """Запись в таблице идентификаторов"""
    name: str
    kind: str = "var"  # var, const, func, class, param
    type_: str = "auto"
    value: Optional[str] = None
    scope: str = "0"  # область видимости
    bucket: int = -1
    pos: int = -1
    line: int = 0  # строка первого появления
    column: int = 0  # колонка первого появления


class IdentifierTable:
    """
    Таблица идентификаторов с хешированием и цепочками.
    Поддерживает вложенные области видимости.
    ИСПРАВЛЕННАЯ ВЕРСИЯ: правильная обработка вложенности
    """
    
    LOAD_FACTOR_THRESHOLD = 0.75
    
    def __init__(self, initial_capacity: int = 128):
        self._capacity = self._next_power_of_two(max(2, initial_capacity))
        self._buckets: List[Optional[List[IdentifierEntry]]] = [None] * self._capacity
        self._count = 0
        self._current_scope = "0"
        self._scope_stack = ["0"]
        self._scope_depth_counter = {}  # счётчик блоков на каждом уровне глубины
        
        # Статистика
        self._total_probes = 0
        self._insertions = 0
        self._searches = 0
        self._collisions = 0
    
    def _next_power_of_two(self, n: int) -> int:
        """Следующая степень 2"""
        p = 1
        while p < n:
            p <<= 1
        return p
    
    def _hash(self, key: str) -> int:
        """Улучшенная хеш-функция (полиномиальное хеширование)"""
        if not key:
            return 0
        h = 0
        for i, ch in enumerate(key):
            # Полиномиальное хеширование с базой 31
            h = (h * 31 + ord(ch)) & 0x7FFFFFFF
        return h % self._capacity
    
    def _is_valid_identifier(self, name: str) -> bool:
        """Проверка корректности идентификатора"""
        if not name:
            return False
        if name[0].isdigit():
            return False
        for ch in name:
            if not (ch.isalnum() or ch == '_'):
                return False
        return True
    
    def _get_scope_depth(self, scope: str) -> int:
        """Получить глубину области видимости"""
        if scope == "0":
            return 0
        # Извлекаем цифры из начала строки
        depth_str = ""
        for ch in scope:
            if ch.isdigit():
                depth_str += ch
            else:
                break
        return int(depth_str) if depth_str else 0
    
    def enter_scope(self) -> str:
        """Войти в новую область видимости (ИСПРАВЛЕНО)"""
        current_depth = self._get_scope_depth(self._current_scope)
        new_depth = current_depth + 1
        
        # Инициализация счётчика для нового уровня глубины
        if new_depth not in self._scope_depth_counter:
            self._scope_depth_counter[new_depth] = 0
        
        block_index = self._scope_depth_counter[new_depth]
        self._scope_depth_counter[new_depth] += 1
        
        # Формирование имени области видимости
        if block_index == 0:
            # Первый блок на этой глубине просто цифра
            new_scope = str(new_depth)
        else:
            # Остальные блоки: цифра + буква (a, b, c, ...)
            letter = chr(ord('a') + block_index - 1)
            new_scope = f"{new_depth}{letter}"
        
        self._scope_stack.append(new_scope)
        self._current_scope = new_scope
        return new_scope
    
    def exit_scope(self) -> Optional[str]:
        """Выйти из текущей области видимости (ИСПРАВЛЕНО)"""
        if len(self._scope_stack) <= 1:
            # Нельзя выходить из глобальной области
            return None
        
        old_scope = self._scope_stack.pop()
        self._current_scope = self._scope_stack[-1]
        return old_scope
    
    def get_current_scope(self) -> str:
        """Получить текущую область видимости"""
        return self._current_scope
    
    def get_scope_stack(self) -> List[str]:
        """Получить стек областей видимости"""
        return self._scope_stack.copy()
    
    def _resize(self) -> None:
        """Увеличить размер таблицы при достижении load factor"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._count = 0
        self._total_probes = 0
        
        # Перехешируем все записи
        for bucket in old_buckets:
            if bucket:
                for entry in bucket:
                    self._insert_entry(entry)
    
    def _insert_entry(self, entry: IdentifierEntry) -> bool:
        """Вспомогательная функция для вставки (при рехешировании)"""
        bi = self._hash(entry.name)
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        entry.bucket = bi
        entry.pos = len(bucket)
        bucket.append(entry)
        self._count += 1
        return True
    
    def insert(self, name: str, kind: str = "var", type_: str = "auto",
              value: Optional[str] = None, line: int = 0, column: int = 0) -> tuple[bool, Optional[str]]:
        """
        Добавить идентификатор в текущую область видимости.
        Возвращает (success: bool, error_message: Optional[str])
        """
        if not name:
            return False, "Пустое имя идентификатора"
        
        if not self._is_valid_identifier(name):
            if name[0].isdigit():
                return False, f"Идентификатор '{name}' не может начинаться с цифры"
            else:
                return False, f"Недопустимые символы в идентификаторе '{name}'"
        
        # Проверка на необходимость увеличения (load factor)
        if (self._count / self._capacity) >= self.LOAD_FACTOR_THRESHOLD:
            self._resize()
        
        bi = self._hash(name)
        self._total_probes += 1
        
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        
        # Проверка на существование в текущей области видимости
        for i, existing_entry in enumerate(bucket):
            self._total_probes += 1
            if existing_entry.name == name and existing_entry.scope == self._current_scope:
                # Запись уже существует в текущей области - обновляем
                existing_entry.kind = kind
                existing_entry.type_ = type_
                existing_entry.value = value
                if line > 0:
                    existing_entry.line = line
                if column > 0:
                    existing_entry.column = column
                return True, None
        
        # Добавление новой записи в текущую область видимости
        entry = IdentifierEntry(
            name=name,
            kind=kind,
            type_=type_,
            value=value,
            scope=self._current_scope,
            bucket=bi,
            pos=len(bucket),
            line=line,
            column=column
        )
        
        bucket.append(entry)
        self._count += 1
        self._insertions += 1
        
        # Подсчёт коллизий
        if len(bucket) > 1:
            self._collisions += 1
        
        return True, None
    
    def search(self, name: str) -> Optional[IdentifierEntry]:
        """
        Поиск идентификатора с учётом областей видимости.
        Ищет сначала в текущей области, потом выше по стеку (к глобальной).
        ИСПРАВЛЕНО: правильная обработка вложенности
        """
        if not name:
            return None
        
        bi = self._hash(name)
        self._total_probes += 1
        self._searches += 1
        
        bucket = self._buckets[bi]
        if not bucket:
            return None
        
        # Поиск по стеку областей видимости (от текущей к глобальной)
        # Ищем в обратном порядке (от более специфичной к менее специфичной)
        for scope_index in range(len(self._scope_stack) - 1, -1, -1):
            target_scope = self._scope_stack[scope_index]
            for entry in bucket:
                self._total_probes += 1
                if entry.name == name and entry.scope == target_scope:
                    return entry
        
        return None
    
    def search_local(self, name: str) -> Optional[IdentifierEntry]:
        """
        Поиск только в текущей области видимости (без поиска в родительских)
        """
        if not name:
            return None
        
        bi = self._hash(name)
        bucket = self._buckets[bi]
        if not bucket:
            return None
        
        for entry in bucket:
            if entry.name == name and entry.scope == self._current_scope:
                return entry
        
        return None
    
    def get_all_entries(self) -> List[IdentifierEntry]:
        """Получить все записи в отсортированном порядке"""
        result = []
        for bucket in self._buckets:
            if bucket:
                result.extend(bucket)
        
        # Сортировка: сначала по области видимости, потом по имени
        def sort_key(entry: IdentifierEntry) -> tuple:
            scope = entry.scope
            if scope == "0":
                depth, letter = 0, ""
            else:
                depth = self._get_scope_depth(scope)
                letter = scope[len(str(depth)):] if len(scope) > len(str(depth)) else ""
            return (depth, letter, entry.name)
        
        return sorted(result, key=sort_key)
    
    def get_entries_by_scope(self, scope: str) -> List[IdentifierEntry]:
        """Получить все записи в определённой области видимости"""
        result = []
        for bucket in self._buckets:
            if bucket:
                for entry in bucket:
                    if entry.scope == scope:
                        result.append(entry)
        return sorted(result, key=lambda e: e.name)
    
    def get_all_scopes(self) -> List[str]:
        """Получить все используемые области видимости"""
        scopes = set()
        for bucket in self._buckets:
            if bucket:
                for entry in bucket:
                    scopes.add(entry.scope)
        
        # Сортировка по глубине и букве
        def scope_sort_key(scope: str) -> tuple:
            if scope == "0":
                return (0, "")
            depth = self._get_scope_depth(scope)
            letter = scope[len(str(depth)):]
            return (depth, letter)
        
        return sorted(scopes, key=scope_sort_key)
    
    def get_scope_tree(self) -> str:
        """Получить визуальное представление иерархии областей видимости"""
        lines = []
        scopes = self.get_all_scopes()
        
        for scope in scopes:
            depth = self._get_scope_depth(scope)
            indent = "  " * depth
            entries = self.get_entries_by_scope(scope)
            entry_names = ", ".join([f"{e.name}({e.kind})" for e in entries])
            lines.append(f"{indent}Область {scope}: [{entry_names}]")
        
        return "\n".join(lines) if lines else "Пусто"
    
    def get_statistics(self) -> str:
        """Получить подробную статистику таблицы (ИСПРАВЛЕНО)"""
        lines = ["=== Статистика таблицы идентификаторов ==="]
        lines.append(f"Размер таблицы: {self._capacity}")
        lines.append(f"Элементов в таблице: {self._count}")
        lines.append(f"Текущая область видимости: {self._current_scope}")
        lines.append(f"Стек областей: {' -> '.join(self._scope_stack)}")
        lines.append(f"Коэффициент загрузки: {self._count / self._capacity:.3f}")
        lines.append(f"Порог для рехеширования: {self.LOAD_FACTOR_THRESHOLD}")
        lines.append("")
        lines.append("=== Операции ===")
        lines.append(f"Вставок: {self._insertions}")
        lines.append(f"Поисков: {self._searches}")
        lines.append(f"Коллизий: {self._collisions}")
        lines.append(f"Всего проб: {self._total_probes}")
        
        ops = self._insertions + self._searches
        if ops > 0:
            lines.append(f"Среднее проб на операцию: {self._total_probes / ops:.2f}")
        
        lines.append("")
        lines.append("=== Распределение бакетов ===")
        non_empty = sum(1 for b in self._buckets if b)
        lines.append(f"Заполненных бакетов: {non_empty} из {self._capacity}")
        
        # Статистика по длинам цепочек
        chain_lengths = {}
        for bucket in self._buckets:
            if bucket:
                length = len(bucket)
                chain_lengths[length] = chain_lengths.get(length, 0) + 1
        
        for length in sorted(chain_lengths.keys()):
            lines.append(f"  Длина {length}: {chain_lengths[length]} бакетов")
        
        return "\n".join(lines)
