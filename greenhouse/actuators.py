class Actuator:
    """Базовый класс для всех исполнительных устройств."""

    def __init__(self, name: str):
        self.name = name
        self.is_active = False  # По умолчанию всё выключено

    def turn_on(self):
        """Включить устройство."""
        self.is_active = True

    def turn_off(self):
        """Выключить устройство."""
        self.is_active = False


class WaterPump(Actuator):
    """Насос для полива."""

    def __init__(self):
        super().__init__("Насос полива")


class Window(Actuator):
    """Сервопривод окна для проветривания."""

    def __init__(self):
        super().__init__("Окно проветривания")


class GrowLight(Actuator):
    """Фитолампа для досветки растений."""

    def __init__(self):
        super().__init__("Лампа освещения")
        