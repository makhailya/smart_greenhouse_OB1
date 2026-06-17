import random


class Sensor:
    """Базовый класс для всех датчиков."""

    def __init__(self, name: str):
        self.name = name  # Имя датчика

    def read(self) -> float:
        """Метод чтения — каждый датчик переопределяет его по-своему."""
        raise NotImplementedError("Каждый датчик должен реализовать метод read()")


class HumiditySensor(Sensor):
    """Датчик влажности почвы (0% — сухо, 100% — мокро)."""

    def __init__(self):
        super().__init__("Датчик влажности")

    def read(self) -> float:
        # Симулируем случайное значение от 20 до 80 процентов
        return round(random.uniform(20, 80), 1)


class TemperatureSensor(Sensor):
    """Датчик температуры воздуха в теплице."""

    def __init__(self):
        super().__init__("Датчик температуры")

    def read(self) -> float:
        # Симулируем от 15 до 40 градусов
        return round(random.uniform(15, 40), 1)


class LightSensor(Sensor):
    """Датчик освещённости в люксах (лк)."""

    def __init__(self):
        super().__init__("Датчик освещённости")

    def read(self) -> int:
        # Симулируем от 100 (пасмурно) до 1000 (солнечно) люкс
        return random.randint(100, 1000)
    