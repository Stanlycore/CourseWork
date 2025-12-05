#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Логгер для отладки транслятора
"""

import logging
import os
from datetime import datetime
from typing import Optional


class TranslatorLogger:
    """Логгер для записи всех этапов трансляции в файл"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.current_log_file: Optional[str] = None
        self.logger: Optional[logging.Logger] = None
        
        # Создаём директорию для логов
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def start_new_session(self) -> str:
        """Начать новую сессию логирования"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.current_log_file = os.path.join(self.log_dir, f"translate_{timestamp}.log")
        
        # Создаём новый logger для этой сессии
        self.logger = logging.getLogger(f"translator_{timestamp}")
        self.logger.setLevel(logging.DEBUG)
        
        # Удаляем старые handlers
        self.logger.handlers = []
        
        # Создаём file handler
        file_handler = logging.FileHandler(self.current_log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Пишем заголовок
        self.logger.info("=" * 80)
        self.logger.info("НОВАЯ СЕССИЯ ТРАНСЛЯЦИИ")
        self.logger.info(f"Файл лога: {self.current_log_file}")
        self.logger.info(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
        
        return self.current_log_file
    
    def debug(self, message: str):
        """Debug сообщение"""
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Info сообщение"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str):
        """Warning сообщение"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str):
        """Error сообщение"""
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message: str):
        """Critical сообщение"""
        if self.logger:
            self.logger.critical(message)
    
    def exception(self, message: str):
        """Логирование исключения"""
        if self.logger:
            self.logger.exception(message)
    
    def separator(self, char: str = "-", length: int = 60):
        """Разделитель"""
        if self.logger:
            self.logger.info(char * length)
    
    def section(self, title: str):
        """Заголовок секции"""
        if self.logger:
            self.logger.info("")
            self.logger.info(f"{'=' * 20} {title} {'=' * 20}")
    
    def close(self):
        """Закрыть текущий лог"""
        if self.logger:
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("СЕССИЯ ЗАВЕРШЕНА")
            self.logger.info("=" * 80)
            
            # Закрываем handlers
            for handler in self.logger.handlers:
                handler.close()
            
            self.logger = None
