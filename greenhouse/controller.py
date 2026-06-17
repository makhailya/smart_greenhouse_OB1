import json
from greenhouse.sensors import HumiditySensor, TemperatureSensor, LightSensor
from greenhouse.actuators import WaterPump, Window, GrowLight
from greenhouse.database import Database


class GreenhouseController:
    """
    Мозг теплицы: читает датчики и принимает решения.
    Логика: если условие нарушено — включить устройство.
    """

    def __init__(self):
        # Загружаем пороговые значения из конфига
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
        self.thresholds = config["thresholds"]

        # Инициализируем датчики
        self.humidity_sensor = HumiditySensor()
        self.temperature_sensor = TemperatureSensor()
        self.light_sensor = LightSensor()

        # Инициализируем исполнители
        self.pump = WaterPump()
        self.window = Window()
        self.lamp = GrowLight()

        # Подключаем базу данных
        self.db = Database()

        # Текущие показания (обновляются при каждом цикле)
        self.humidity = 0.0
        self.temperature = 0.0
        self.light = 0

    def read_sensors(self):
        """Читает все датчики и сохраняет показания в БД."""
        self.humidity = self.humidity_sensor.read()
        self.temperature = self.temperature_sensor.read()
        self.light = self.light_sensor.read()
        self.db.log_sensors(self.humidity, self.temperature, self.light)

    def control(self):
        """Основной цикл управления: читает датчики и принимает решения."""
        self.read_sensors()
        self._control_watering()
        self._control_ventilation()
        self._control_lighting()

    def _control_watering(self):
        """Управление поливом: включить, если влажность ниже минимума."""
        if self.humidity < self.thresholds["humidity_min"]:
            if not self.pump.is_active:  # Включаем только если ещё не включён
                self.pump.turn_on()
                self.db.log_event(
                    f"Насос ВКЛЮЧЁН — влажность {self.humidity}% "
                    f"(порог: {self.thresholds['humidity_min']}%)"
                )
        else:
            if self.pump.is_active:  # Выключаем только если был включён
                self.pump.turn_off()
                self.db.log_event(
                    f"Насос ВЫКЛЮЧЕН — влажность восстановлена до {self.humidity}%"
                )

    def _control_ventilation(self):
        """Управление проветриванием: открыть окно, если жарко."""
        if self.temperature > self.thresholds["temperature_max"]:
            if not self.window.is_active:
                self.window.turn_on()
                self.db.log_event(
                    f"Окно ОТКРЫТО — температура {self.temperature}°C "
                    f"(порог: {self.thresholds['temperature_max']}°C)"
                )
        else:
            if self.window.is_active:
                self.window.turn_off()
                self.db.log_event(
                    f"Окно ЗАКРЫТО — температура упала до {self.temperature}°C"
                )

    def _control_lighting(self):
        """Управление освещением: включить лампу, если темно."""
        if self.light < self.thresholds["light_min"]:
            if not self.lamp.is_active:
                self.lamp.turn_on()
                self.db.log_event(
                    f"Лампа ВКЛЮЧЕНА — освещённость {self.light} лк "
                    f"(порог: {self.thresholds['light_min']} лк)"
                )
        else:
            if self.lamp.is_active:
                self.lamp.turn_off()
                self.db.log_event(
                    f"Лампа ВЫКЛЮЧЕНА — освещённость {self.light} лк"
                )
                