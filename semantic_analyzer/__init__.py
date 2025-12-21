#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль семантического анализа
"""

from .semantic_analyzer import SemanticAnalyzer
from .errors import SemanticError, ErrorType

__all__ = ['SemanticAnalyzer', 'SemanticError', 'ErrorType']
