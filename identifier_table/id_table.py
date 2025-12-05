#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Таблица идентификаторов с поддержкой областей видимости
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


class IdentifierTable:
    """
    Таблица идентификаторов с хешированием и цепочками.
    Поддерживает вложенные области видимости.
    """
    
    LOAD_FACTOR_THRESHOLD = 0.75
    
    def __init__(self, initial_capacity: int = 128):
        self._capacity = self._next_power_of_two(max(2, initial_capacity))
        self._buckets: List[Optional[List[IdentifierEntry]]] = [None] * self._capacity
        self._count = 0
        self._current_scope = "0"
        self._scope_stack = ["0"]
        self._depth_block_counters: Dict[int, int] = {}
        
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
        """Хеш-функция"""
        if not key:
            return 0
        h = 0
        for ch in key:
            h = ((h << 5) - h + ord(ch)) & 0x7FFFFFFF
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
        depth_str = ""
        for ch in scope:
            if ch.isdigit():
                depth_str += ch
            else:
                break
        return int(depth_str) if depth_str else 0
    
    def enter_scope(self) -> str:
        """Войти в новую область видимости"""
        current_depth = self._get_scope_depth(self._current_scope)
        new_depth = current_depth + 1
        
        if new_depth not in self._depth_block_counters:
            self._depth_block_counters[new_depth] = 0
        
        block_number = self._depth_block_counters[new_depth]
        self._depth_block_counters[new_depth] += 1
        
        if block_number == 0:
            new_scope = str(new_depth)
        else:
            letter = chr(ord('a') + block_number - 1)
            new_scope = f"{new_depth}{letter}"
        
        self._scope_stack.append(new_scope)
        self._current_scope = new_scope
        return new_scope
    
    def exit_scope(self) -> Optional[str]:
        """Выйти из текущей области видимости"""
        if len(self._scope_stack) <= 1:
            return None
        
        old_scope = self._scope_stack.pop()
        self._current_scope = self._scope_stack[-1]
        return old_scope
    
    def get_current_scope(self) -> str:
        """Получить текущую область видимости"""
        return self._current_scope
    
    def _resize(self) -> None:
        """Увеличить размер таблицы"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._count = 0
        
        for bucket in old_buckets:
            if bucket:
                for e in bucket:
                    self._insert_entry(e)
    
    def _insert_entry(self, entry: IdentifierEntry) -> bool:
        """Вспомогательная функция для вставки"""
        bi = self._hash(entry.name)
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        entry.bucket, entry.pos = bi, len(bucket)
        bucket.append(entry)
        self._count += 1
        return True
    
    def insert(self, name: str, kind: str = "var", type_: str = "auto",
              value: Optional[str] = None) -> tuple[bool, Optional[str]]:
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
        
        # Проверка на необходимость увеличения
        if (self._count / self._capacity) >= self.LOAD_FACTOR_THRESHOLD:
            self._resize()
        
        bi = self._hash(name)
        self._total_probes += 1
        
        if self._buckets[bi] is None:
            self._buckets[bi] = []
        
        bucket = self._buckets[bi]
        
        # Проверка на существование в текущей области
        for i, ex in enumerate(bucket):
            self._total_probes += 1
            if ex.name == name and ex.scope == self._current_scope:
                # Обновление существующей записи
                ex.kind = kind
                ex.type_ = type_
                ex.value = value
                return True, None
        
        # Добавление новой записи
        entry = IdentifierEntry(
            name=name, kind=kind, type_=type_, value=value,
            scope=self._current_scope, bucket=bi, pos=len(bucket)
        )
        
        bucket.append(entry)
        self._count += 1
        self._insertions += 1
        
        if len(bucket) > 1:
            self._collisions += 1
        
        return True, None
    
    def search(self, name: str) -> Optional[IdentifierEntry]:
        """
        Поиск идентификатора с учетом областей видимости.
        Ищет сначала в текущей области, потом выше по стеку.
        """
        if not name:
            return None
        
        bi = self._hash(name)
        self._total_probes += 1
        self._searches += 1
        
        bucket = self._buckets[bi]
        if not bucket:
            return None
        
        # Поиск по стеку областей (от текущей к глобальной)
        for scope_level in reversed(self._scope_stack):
            for e in bucket:
                self._total_probes += 1
                if e.name == name and e.scope == scope_level:
                    return e
        
        return None
    
    def get_all_entries(self) -> List[IdentifierEntry]:
        """Получить все записи"""
        result = []
        for bucket in self._buckets:
            if bucket:
                result.extend(bucket)
        
        def scope_sort_key(entry: IdentifierEntry) -> tuple:
            scope = entry.scope
            if scope == "0":
                return (0, "")
            depth = self._get_scope_depth(scope)
            letter = scope[len(str(depth)):] if len(scope) > len(str(depth)) else ""
            return (depth, letter)
        
        return sorted(result, key=lambda e: (scope_sort_key(e), e.name))
    
    def get_all_scopes(self) -> List[str]:
        """Получить все используемые области видимости"""
        scopes = set()
        for bucket in self._buckets:
            if bucket:
                for entry in bucket:
                    scopes.add(entry.scope)
        
        return sorted(scopes, key=lambda s: (self._get_scope_depth(s), s))
    
    def get_statistics(self) -> str:
        """Получить статистику таблицы"""
        lines = ["=== Статистика таблицы идентификаторов ==="]
        lines.append(f"Размер таблицы: {self._capacity}")
        lines.append(f"Элементов: {self._count}")
        lines.append(f"Текущая область видимости: {self._current_scope}")
        lines.append(f"Стек областей: {self._scope_stack}")
        lines.append(f"Коэффициент загрузки: {self._count / self._capacity:.3f}")
        lines.append(f"Вставок: {self._insertions}")
        lines.append(f"Поисков: {self._searches}")
        lines.append(f"Коллизий: {self._collisions}")
        lines.append(f"Всего проб: {self._total_probes}")
        
        ops = self._insertions + self._searches
        if ops:
            lines.append(f"Среднее проб: {self._total_probes / ops:.2f}")
        
        return "\n".join(lines)
