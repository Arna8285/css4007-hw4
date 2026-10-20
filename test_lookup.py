
# Импортируем функцию поиска
from tools_hw4 import lookup

# Проверяем население района
def test_population():
    assert lookup("Brightwater", "population_2025")["value"] == 44675

# Проверяем исправленную площадь
def test_corrected_area():
    assert lookup("Brightwater", "area_km2")["value"] == 921.4

# Проверяем перевод воды в мегалитры
def test_water_conversion():
    assert lookup("Lindenmoor", "water_2025")["value"] == 2151.4

# Проверяем бюджет района
def test_budget():
    assert lookup("Millbrook", "budget_2025")["value"] == 6305.7

# Проверяем источник исправленных данных
def test_correct_source():
    assert lookup("Brightwater", "area_km2")["source"] == "NR-16"

# Проверяем неправильное название района
def test_unknown_district():
    assert "error" in lookup("Ossbrige", "population_2025")

# Проверяем неизвестное поле
def test_unknown_field():
    assert "error" in lookup("Brightwater", "unknown_field")
