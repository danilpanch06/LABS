"""Юнит-тесты для модулей validators и operations."""
import math  # подключаем математику (нужна для проверки логарифма math.log)
import unittest  # подключаем встроенный инструмент для запуска автотестов
from unittest.mock import patch  # инструмент для подмены ввода с клавиатуры (input)

import logger  # подключаем наш модуль журнала ошибок
from constants import (  # берём константы границ и коэффициентов из constants.py
    K_CERAMIC,
    K_GRAIN,
    K_WOOD,
    M_MAX,
    M_MIN,
    T_MAX,
    T_MIN,
    W1_MAX,
    W1_MIN,
)
from operations import drying_class, drying_time, water_mass  # наши расчётные функции
from validators import (  # наши функции проверки ввода
    input_mass,
    input_temperature,
    input_w1,
    input_w2,
    validate_range,
)


# Создаём группу тестов (класс) для проверки границ диапазона
class TestValidateRange(unittest.TestCase):
    """Тесты проверки попадания значения в диапазон."""

    # Имя каждого теста обязано начинаться со слова test_
    def test_inside_range(self) -> None:
        # assertEqual проверяет, что результат функции строго равен (True, "")
        self.assertEqual(validate_range(50.0, 1.0, 100.0), (True, ""))

    def test_on_lower_bound(self) -> None:
        # Проверяем ровно нижнюю границу (1.0 при минимуме 1.0)
        self.assertEqual(validate_range(1.0, 1.0, 100.0), (True, ""))

    def test_on_upper_bound(self) -> None:
        # Проверяем ровно верхнюю границу (100.0 при максимуме 100.0)
        self.assertEqual(validate_range(100.0, 1.0, 100.0), (True, ""))

    def test_below_lower_bound(self) -> None:
        # Передаём число меньше минимума (0.5 < 1.0)
        ok, msg = validate_range(0.5, 1.0, 100.0)
        self.assertFalse(ok)  # assertFalse проверяет, что функция вернула False (ошибку)
        self.assertIn("меньше", msg)  # assertIn проверяет, что в тексте ошибки есть слово "меньше"

    def test_above_upper_bound(self) -> None:
        # Передаём число больше максимума (105.0 > 100.0)
        ok, msg = validate_range(105.0, 1.0, 100.0)
        self.assertFalse(ok)  # ждём False
        self.assertIn("больше", msg)  # ждём слово "больше" в сообщении об ошибке


# Группа тестов для проверки функций ввода (где есть input и цикл while)
class TestInputValidators(unittest.TestCase):
    """Тесты циклического ввода и обработки ошибок."""

    # setUp — служебная функция, Python запускает её САМ перед каждым тестом
    def setUp(self) -> None:
        logger.clear()  # очищаем журнал ошибок, чтобы старые записи не мешали новому тесту

    # @patch подменяет input() внутри validators.py на список готовых ответов из side_effect
    @patch("validators.input", side_effect=["abc", "6000", "250"])
    def test_input_mass_cyclic(self, _mock_input) -> None:
        # Робот по очереди введёт: "abc" (ошибка), "6000" (много), "250" (верно)
        result = input_mass()
        self.assertEqual(result, 250.0)  # убеждаемся, что в итоге вернулось число 250.0
        self.assertEqual(len(logger.get_entries()), 2)  # проверяем, что в лог записались ровно 2 ошибки

    @patch("validators.input", side_effect=[str(M_MIN), str(M_MAX)])
    def test_input_mass_bounds(self, _mock_input) -> None:
        # Проверяем, что граничные значения массы (1.0 и 5000.0) принимаются с первого раза
        self.assertEqual(input_mass(), M_MIN)
        self.assertEqual(input_mass(), M_MAX)

    @patch("validators.input", side_effect=["2", "80", "25"])
    def test_input_w1_cyclic(self, _mock_input) -> None:
        # Вводим для w1: "2" (меньше 5), "80" (больше 60), "25" (верно)
        result = input_w1()
        self.assertEqual(result, 25.0)
        self.assertEqual(len(logger.get_entries()), 2)  # в логе должно быть 2 ошибки

    @patch("validators.input", side_effect=[str(W1_MIN), str(W1_MAX)])
    def test_input_w1_bounds(self, _mock_input) -> None:
        # Проверяем граничные значения начальной влажности (5.0 и 60.0)
        self.assertEqual(input_w1(), W1_MIN)
        self.assertEqual(input_w1(), W1_MAX)

    @patch("validators.input", side_effect=["0", "25", "15"])
    def test_input_w2_cyclic(self, _mock_input) -> None:
        # При w1 = 20.0 вводим: "0" (нельзя <= 0), "25" (нельзя >= w1), "15" (верно)
        result = input_w2(20.0)
        self.assertEqual(result, 15.0)
        self.assertEqual(len(logger.get_entries()), 2)  # в логе должно быть 2 ошибки

    @patch("validators.input", side_effect=["10", "500", "120"])
    def test_input_temperature_cyclic(self, _mock_input) -> None:
        # Вводим температуру: "10" (мало), "500" (много), "120" (верно)
        result = input_temperature()
        self.assertEqual(result, 120.0)
        self.assertEqual(len(logger.get_entries()), 2)  # в логе должно быть 2 ошибки

    @patch("validators.input", side_effect=[str(T_MIN), str(T_MAX)])
    def test_input_temperature_bounds(self, _mock_input) -> None:
        # Проверяем граничные значения температуры (40.0 и 250.0)
        self.assertEqual(input_temperature(), T_MIN)
        self.assertEqual(input_temperature(), T_MAX)


# Группа тестов для проверки формул и классификации
class TestOperations(unittest.TestCase):
    """Тесты расчётных функций и классификации."""

    def test_water_mass(self) -> None:
        # assertAlmostEqual сравнивает дробные числа с точностью до 4 знаков после запятой (places=4)
        self.assertAlmostEqual(water_mass(100.0, 25.0, 10.0), 16.6667, places=4)

    def test_drying_time_wood(self) -> None:
        # Считаем эталонный ответ по формуле для древесины и сравниваем с нашей функцией
        expected = (1 / K_WOOD) * math.log(20.0 / 10.0)
        self.assertAlmostEqual(drying_time(K_WOOD, 20.0, 10.0), expected, places=4)

    def test_drying_time_ceramic(self) -> None:
        # То же самое для керамики
        expected = (1 / K_CERAMIC) * math.log(20.0 / 10.0)
        self.assertAlmostEqual(drying_time(K_CERAMIC, 20.0, 10.0), expected, places=4)

    def test_drying_time_grain(self) -> None:
        # То же самое для зерна
        expected = (1 / K_GRAIN) * math.log(20.0 / 10.0)
        self.assertAlmostEqual(drying_time(K_GRAIN, 20.0, 10.0), expected, places=4)

    def test_drying_class_fast(self) -> None:
        # Меньше 2 часов -> быстрая сушка
        self.assertEqual(drying_class(1.5), "быстрая сушка")

    def test_drying_class_lower_boundary(self) -> None:
        # Ровно 2 часа -> нормальная сушка
        self.assertEqual(drying_class(2.0), "нормальная сушка")

    def test_drying_class_normal(self) -> None:
        # От 2 до 12 часов -> нормальная сушка
        self.assertEqual(drying_class(7.0), "нормальная сушка")

    def test_drying_class_upper_boundary(self) -> None:
        # Ровно 12 часов -> нормальная сушка
        self.assertEqual(drying_class(12.0), "нормальная сушка")

    def test_drying_class_long(self) -> None:
        # Больше 12 часов -> длительная сушка
        self.assertEqual(drying_class(15.0), "длительная сушка")


# Точка запуска: если запустить этот файл напрямую, выполнятся все тесты выше
if __name__ == "__main__":
    unittest.main()