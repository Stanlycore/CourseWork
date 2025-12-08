#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры Python2 программ для тестирования транслятора
10 рабочих примеров + 2 примера с ошибками
"""

EXAMPLES = {
    "01. Print функция": '''# Python 2: print это оператор
# Python 3: print это функция
print "Hello, World!"
print "The answer is", 42
print "Without newline",
x = 10
print "x =", x
''',

    "02. Неравенство <> -> !=": '''# Оператор неравенства
# Python 2: можно использовать <> или !=
# Python 3: только !=
x = 5
y = 3

if x <> y:
    print "x not equal y"

if x != y:
    print "Alternative: not equal"
''',

    "03. xrange -> range": '''# Диапазон и итерация
# Python 2: xrange (ленивый), range (создает список)
# Python 3: range (ленивый, как xrange)
print "Counting with range:"
for i in xrange(5):
    print i

print "\nList from range:"
for j in range(1, 4):
    print j
''',

    "04. Dict методы: iterkeys, itervalues, iteritems": '''# Методы словаря
# Python 2: iterkeys(), itervalues(), iteritems() - ленивые
# Python 3: keys(), values(), items() - ленивые
my_dict = {"a": 1, "b": 2, "c": 3}

print "Keys:"
for key in my_dict.iterkeys():
    print key

print "\nValues:"
for value in my_dict.itervalues():
    print value

print "\nItems:"
for k, v in my_dict.iteritems():
    print k, ":", v
''',

    "05. raw_input -> input": '''# Функции ввода
# Python 2: raw_input() для строк, input() для выражений
# Python 3: input() для строк, eval(input()) для выражений
name = raw_input("Enter your name: ")
print "Hello,", name

print "Type a number:"
value = raw_input()
print "You entered:", value
''',

    "06. Списки, кортежи, словари": '''# Коллекции
# Синтаксис одинаков в Python2 и Python3
list_data = [1, 2, 3, 4, 5]
tuple_data = (10, 20, 30)
dict_data = {"x": 100, "y": 200}

print "List:", list_data
print "Tuple:", tuple_data
print "Dict:", dict_data

print "\nAccessing:"
print "list_data[0] =", list_data[0]
print "tuple_data[1] =", tuple_data[1]
print "dict_data['x'] =", dict_data['x']
''',

    "07. Класс и объекты": '''# Классы и атрибуты
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        print "Hello, my name is", self.name
        print "I am", self.age, "years old"
    
    def birthday(self):
        self.age = self.age + 1
        print "Happy birthday!"

p1 = Person("Alice", 25)
p1.greet()
p1.birthday()
p1.greet()
''',

    "08. Вложенные циклы и логика": '''# Вложенные циклы с условиями
print "Nested loops:"
for i in xrange(3):
    print "\nOuter loop:", i
    for j in xrange(3):
        if i * j > 0:
            print "  Inner:", i, "*", j, "=", i * j
        else:
            print "  Skip (zero)"
''',

    "09. Функции с возвратом": '''# Рекурсивные функции
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

print "5! =", factorial(5)
print "Fibonacci(7) =", fibonacci(7)
''',

    "10. Комплексная программа - Калькулятор": '''# Калькулятор с функциями
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        print "Error: division by zero"
        return 0
    else:
        return x / y

print "Calculator:"
print "10 + 5 =", add(10, 5)
print "10 - 5 =", subtract(10, 5)
print "10 * 5 =", multiply(10, 5)
print "10 / 5 =", divide(10, 5)
print "10 / 0 =", divide(10, 0)
''',

    "11. Ошибка: неверный синтаксис if": '''# Синтаксическая ошибка: отсутствует двоеточие
if x < 10
    print "x is less than 10"

for i in range(5)
    print i
''',

    "12. Ошибка: неверный отступ": '''# Ошибка отступа
def test():
print "Missing indentation"
  print "Wrong indentation"

test()
''',
}
