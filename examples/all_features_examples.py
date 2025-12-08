#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полные примеры транслятора Python 2 → Python 3

ГРУППА 1: Основные операторы
===============================================
"""

# Пример 1: print как функция
# Преображения: print оператор → print() функция
print "Hello, World"
print "Number:", 42
print "A",  # без переноса строки

# Пример 2: Неравенство <>
# Преображения: <> → !=
x = 5
y = 3
if x <> y:
    print "x not equal y"
else:
    print "x equal y"

# Пример 3: xrange → range
# Преображения: xrange → range, print() функция
for i in xrange(3):
    print "Index:", i

# Пример 4: Логические операторы and/or/not
# Преображения: Логика работает так же
a = 10
b = 20
if a > 5 and b > 15:
    print "Both conditions true"
if a < 5 or b > 15:
    print "At least one condition true"
if not (a == 0):
    print "a is not zero"

# Пример 5: Атрибуты и индексация (obj.attr, obj[index])
# Преображения: obj.attr и obj[index] работают так же
class Point:
    def __init__(self):
        self.x = 10
        self.y = 20

p = Point()
print p.x
print p.y

arr = [1, 2, 3, 4, 5]
print arr[0]
print arr[2]

"""
ГРУППА 2: Методы словарей и диапазонов
===============================================
"""

# Пример 6: dict.iterkeys/itervalues/iteritems → keys/values/items
# Преображения: iterkeys() → keys(), itervalues() → values(), iteritems() → items()
my_dict = {"a": 1, "b": 2, "c": 3}

print "Keys:"
for key in my_dict.iterkeys():
    print key

print "Values:"
for value in my_dict.itervalues():
    print value

print "Items:"
for key, value in my_dict.iteritems():
    print key, ":", value

# Пример 7: dict.has_key(k) → k in dict
# Преображения: has_key(k) → k in dict
if my_dict.has_key("a"):
    print "Key 'a' exists"

if "b" in my_dict:
    print "Key 'b' exists"

"""
ГРУППА 3: Встроенные типы данных
===============================================
"""

# Пример 8: raw_input → input, строки unicode
# Преображения: raw_input() → input(), u"" → ""
name = raw_input("Enter name: ")
greeting = u"Hello, " + name
print greeting

# Пример 9: Числа с суффиксом L
# Преображения: 123L → 123 (суффикс удаляется лексером)
big_number = 999999999999999999L
print big_number

# Пример 10: Преображения типов
# Преображения: unicode() → str(), unichr() → chr(), file() → open()
text = unicode("Hello")
print text

char_code = unichr(65)
print char_code

"""
ОШИБКА 1: Неожиданный DOT при атрибуте
===============================================
Описание: Ошибка - пропущен токен где-то
"""

# ОШИБКА 1a: Point without dot
class Point:
    x = 10

p = Point()
# print p x  # ОШИБКА: нет точки, где должна быть точка

"""
ОШИБКА 2: Незакрытое выражение
===============================================
Описание: Ошибка парсинга - нехватает закрывающего символа
"""

# ОШИБКА 2a: Missing closing bracket
arr = [1, 2, 3
# print arr[0]  # ОШИБКА: не закрыт массив
