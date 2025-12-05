#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры Python2 программ для тестирования
"""

EXAMPLES = {
    "Пример 1: Print статемент": '''
# Python 2 print statement
print "Hello, World!"
print "The answer is", 42
x = 10
print "x =", x
''',

    "Пример 2: Функция и цикл": '''
# Простая функция
def greet(name):
    print "Hello,", name

# Цикл
for i in range(5):
    greet("User")
    print "Iteration:", i
''',

    "Пример 3: Условные операторы": '''
# Условные операторы
x = 10
y = 20

if x < y:
    print "x меньше y"
elif x == y:
    print "x равно y"
else:
    print "x больше y"
''',

    "Пример 4: Вложенные циклы": '''
# Вложенные циклы
for i in range(3):
    print "\nВнешний цикл:", i
    for j in range(3):
        print "  Внутренний цикл:", j
        result = i * j
        print "  Результат:", result
''',

    "Пример 5: Функция с возвратом": '''
# Функция с возвратом
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

print "5! =", factorial(5)
print "10! =", factorial(10)
''',

    "Пример 6: Работа со списками": '''
# Работа со списками
numbers = range(1, 11)
total = 0

for num in numbers:
    total = total + num
    print "Число:", num
    print "Сумма:", total

print "\nИтоговая сумма:", total
''',

    "Пример 7: Класс и объекты": '''
# Простой класс
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        print "Hello, my name is", self.name
        print "I am", self.age, "years old"

p1 = Person("Alice", 25)
p1.greet()

p2 = Person("Bob", 30)
p2.greet()
''',

    "Пример 8: While цикл": '''
# While цикл
counter = 0
max_count = 5

while counter < max_count:
    print "Счетчик:", counter
    counter = counter + 1

print "Цикл завершен"
''',

    "Пример 9: Математические операции": '''
# Математические вычисления
a = 10
b = 3

print "a + b =", a + b
print "a - b =", a - b
print "a * b =", a * b
print "a / b =", a / b
print "a % b =", a % b
print "a ** b =", a ** b
''',

    "Пример 10: Сложная программа": '''
# Калькулятор с функциями
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        print "Ошибка: деление на ноль"
        return None
    else:
        return x / y

print "10 + 5 =", add(10, 5)
print "10 - 5 =", subtract(10, 5)
print "10 * 5 =", multiply(10, 5)
print "10 / 5 =", divide(10, 5)
print "10 / 0 =", divide(10, 0)
''',

    "❌ Пример 11: Ошибки (неверный отступ)": '''
# Некорректный отступ
def test():
print "This will cause error"
  print "Incorrect indentation"
''',

    "❌ Пример 12: Ошибки (синтаксис)": '''
# Синтаксические ошибки
if x < 10
    print "Missing colon"

for i in range(5)
    print i
'''
}
