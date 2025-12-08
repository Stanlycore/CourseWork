#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полные примеры транслятора Python 2 → Python 3

ГРУППА 1: Основные операторы
===============================================
"""

# Пример 1: print как функция
# Преображения: print оператор → print() функция
print "Hello, World!"
print "Number:", 42

# Пример 2: Неравенство <>
# Преображения: <> → !=
x = 5
y = 3
if x <> y:
    print "x not equal y"

# Пример 3: xrange → range
# Преображения: xrange → range
for i in xrange(3):
    print "Index:", i

# Пример 4: Логические операторы and/or/not
# Преображения: Логика работает так же
a = 10
b = 20
if a > 5 and b > 15:
    print "Both true"
if not (a == 0):
    print "a is not zero"

# Пример 5: Атрибуты и методы (obj.attr, obj.method())
# Преображения: obj.attr и obj.method() работают так же
class Point:
    def __init__(self):
        self.x = 10
        self.y = 20

p = Point()
print p.x
print p.y

# Пример 6: Индексация списков (obj[index])
# Преображения: obj[index] работает так же
arr = [1, 2, 3, 4, 5]
print arr[0]
print arr[2]

# Пример 7: dict.iterkeys/itervalues/iteritems → keys/values/items
# Преображения: iterkeys → keys, itervalues → values, iteritems → items
my_dict = {"a": 1, "b": 2, "c": 3}

for key in my_dict.iterkeys():
    print key

for value in my_dict.itervalues():
    print value

for k, v in my_dict.iteritems():
    print k, ":", v

# Пример 8: raw_input → input
# Преображения: raw_input() → input()
name = raw_input("Enter name: ")
print "Hello", name

# Пример 9: Числа с суффиксом L
# Преображения: 123L → 123 (суффикс удаляется лексером)
big_number = 999999999999999999L
print big_number

# Пример 10: Списки, словари, кортежи
# Преображения: Никаких преобразований, сравниваются так же
list_data = [10, 20, 30]
tuple_data = (1, 2, 3)
dict_data = {"x": 100, "y": 200}

print list_data
print tuple_data
print dict_data

"""
ОШИБКА 1: Неожиданный символ
===============================================
"""

# ОШИБКА 1a: Неравенство в иде ><
a = 5
if a >< 3:
    print "error"

"""
ОШИБКА 2: Незакрытые скобки
===============================================
"""

# ОШИБКА 2a: Незакрытые скобки
arr = [1, 2, 3
print arr[0]
