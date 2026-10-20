
# Импортируем функцию калькулятора из основного файла
from tools_hw4 import calculate

# Проверяем сложение
def test_addition():
    assert calculate("10 + 20")["result"] == 30

# Проверяем умножение
def test_multiplication():
    assert calculate("5 * 6")["result"] == 30

# Проверяем деление
def test_division():
    assert calculate("100 / 4")["result"] == 25

# Проверяем отрицательные числа
def test_negative_numbers():
    assert calculate("-10 + 3")["result"] == -7

# Проверяем деление на ноль
def test_zero_division():
    assert "error" in calculate("10 / 0")

# Проверяем блокировку опасного Python-кода
def test_dangerous_input():
    assert "error" in calculate("__import__('os').system('echo hacked')")

# Проверяем запрет на возведение в степень
def test_unsupported_operation():
    assert "error" in calculate("2 ** 100")
