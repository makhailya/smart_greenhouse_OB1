import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from greenhouse.controller import GreenhouseController


class GreenhouseApp:
    """Графический интерфейс умной теплицы."""

    UPDATE_INTERVAL = 3000  # Обновление каждые 3 секунды (в мс)
    WATERING_SCHEDULE = ["08:00", "12:00", "18:00"]  # Расписание полива

    def __init__(self):
        self.controller = GreenhouseController()
        self.last_scheduled_watering = None  # Чтобы не поливать дважды в одну минуту

        # Создаём главное окно
        self.root = tk.Tk()
        self.root.title("🌱 Умная теплица")
        self.root.geometry("720x580")
        self.root.configure(bg="#1a2e23")
        self.root.resizable(False, False)

        self._build_ui()

    # ──────────────────────────────────────────
    # Построение интерфейса
    # ──────────────────────────────────────────

    def _build_ui(self):
        """Собирает весь интерфейс."""
        self._build_title()
        self._build_panels()
        self._build_log()
        self._build_status_bar()

    def _build_title(self):
        tk.Label(
            self.root,
            text="🌱  УМНАЯ ТЕПЛИЦА",
            font=("Arial", 22, "bold"),
            bg="#1a2e23", fg="#76ff7a"
        ).pack(pady=(12, 4))

    def _build_panels(self):
        """Создаёт два блока: датчики и управление."""
        container = tk.Frame(self.root, bg="#1a2e23")
        container.pack(fill="x", padx=20, pady=6)

        # ── Блок датчиков ──
        sensor_frame = tk.LabelFrame(
            container, text="📊 Датчики",
            bg="#1a2e23", fg="#76ff7a",
            font=("Arial", 11, "bold"), padx=10, pady=8
        )
        sensor_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.humidity_lbl  = self._sensor_row(sensor_frame, 0, "💧 Влажность:")
        self.temp_lbl      = self._sensor_row(sensor_frame, 1, "🌡  Температура:")
        self.light_lbl     = self._sensor_row(sensor_frame, 2, "☀️  Освещённость:")

        # ── Блок управления ──
        actuator_frame = tk.LabelFrame(
            container, text="⚙️  Управление",
            bg="#1a2e23", fg="#76ff7a",
            font=("Arial", 11, "bold"), padx=10, pady=8
        )
        actuator_frame.grid(row=0, column=1, sticky="nsew")

        self.pump_lbl   = self._actuator_row(actuator_frame, 0, "💧 Насос:",   self._toggle_pump)
        self.window_lbl = self._actuator_row(actuator_frame, 1, "🌬  Окно:",    self._toggle_window)
        self.lamp_lbl   = self._actuator_row(actuator_frame, 2, "💡 Лампа:",   self._toggle_lamp)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

    @staticmethod
    def _sensor_row(parent, row: int, text: str) -> tk.Label:
        """Создаёт строку с названием датчика и значением."""
        tk.Label(parent, text=text, bg="#1a2e23", fg="white",
                 font=("Arial", 11), anchor="w").grid(row=row, column=0, sticky="w", pady=5)
        lbl = tk.Label(parent, text="--", bg="#1a2e23", fg="#4fc3f7",
                       font=("Arial", 13, "bold"), width=10)
        lbl.grid(row=row, column=1, padx=8)
        return lbl

    @staticmethod
    def _actuator_row(parent, row: int, text: str, command) -> tk.Label:
        """Создаёт строку с названием устройства, статусом и кнопкой."""
        tk.Label(parent, text=text, bg="#1a2e23", fg="white",
                 font=("Arial", 11), anchor="w").grid(row=row, column=0, sticky="w", pady=5)
        lbl = tk.Label(parent, text="ВЫКЛ", bg="#1a2e23", fg="#ff5252",
                       font=("Arial", 12, "bold"), width=9)
        lbl.grid(row=row, column=1, padx=6)
        tk.Button(parent, text="Вкл / Выкл", command=command,
                  bg="#2d5a3d", fg="white", relief="flat",
                  padx=6).grid(row=row, column=2, padx=4)
        return lbl

    def _build_log(self):
        log_frame = tk.LabelFrame(
            self.root, text="📋 Журнал событий",
            bg="#1a2e23", fg="#76ff7a",
            font=("Arial", 11, "bold")
        )
        log_frame.pack(fill="both", expand=True, padx=20, pady=6)

        self.log_box = scrolledtext.ScrolledText(
            log_frame, height=10,
            bg="#0c1f15", fg="#a5d6a7",
            font=("Courier", 10), state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Инициализация...")
        tk.Label(
            self.root, textvariable=self.status_var,
            bg="#0c1f15", fg="#76ff7a", font=("Arial", 9), anchor="w"
        ).pack(fill="x", side="bottom", padx=6)

    # ──────────────────────────────────────────
    # Ручное управление (кнопки)
    # ──────────────────────────────────────────

    def _toggle_pump(self):
        self._toggle(self.controller.pump, "Насос")

    def _toggle_window(self):
        self._toggle(self.controller.window, "Окно")

    def _toggle_lamp(self):
        self._toggle(self.controller.lamp, "Лампа")

    def _toggle(self, device, name: str):
        """Переключает устройство вручную и пишет событие в БД."""
        if device.is_active:
            device.turn_off()
            self.controller.db.log_event(f"{name} ВЫКЛЮЧЕН(а) вручную")
        else:
            device.turn_on()
            self.controller.db.log_event(f"{name} ВКЛЮЧЁН(а) вручную")
        self._refresh_actuators()
        self._refresh_log()

    # ──────────────────────────────────────────
    # Обновление данных на экране
    # ──────────────────────────────────────────

    def _refresh_sensors(self):
        """Обновляет числа и цвета датчиков."""
        th = self.controller.thresholds

        self.humidity_lbl.config(
            text=f"{self.controller.humidity} %",
            fg="#ff5252" if self.controller.humidity < th["humidity_min"] else "#69f0ae"
        )
        self.temp_lbl.config(
            text=f"{self.controller.temperature} °C",
            fg="#ff5252" if self.controller.temperature > th["temperature_max"] else "#69f0ae"
        )
        self.light_lbl.config(
            text=f"{self.controller.light} лк",
            fg="#ff5252" if self.controller.light < th["light_min"] else "#69f0ae"
        )

    def _refresh_actuators(self):
        """Обновляет статусы устройств."""
        def update(label, device, on_text="ВКЛ", off_text="ВЫКЛ"):
            label.config(
                text=on_text if device.is_active else off_text,
                fg="#69f0ae" if device.is_active else "#ff5252"
            )

        update(self.pump_lbl,   self.controller.pump)
        update(self.window_lbl, self.controller.window, "ОТКРЫТО", "ЗАКРЫТО")
        update(self.lamp_lbl,   self.controller.lamp)

    def _refresh_log(self):
        """Загружает последние события из БД и выводит в журнал."""
        events = self.controller.db.get_recent_events(limit=20)
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        for timestamp, event in reversed(events):
            time_str = timestamp[11:19]  # Берём только HH:MM:SS из ISO строки
            self.log_box.insert("end", f"[{time_str}]  {event}\n")
        self.log_box.config(state="disabled")
        self.log_box.see("end")  # Прокручиваем вниз

    # ──────────────────────────────────────────
    # Расписание полива
    # ──────────────────────────────────────────

    def _check_schedule(self):
        """Проверяет, не пора ли поливать по расписанию."""
        now = datetime.now()
        current_hm = now.strftime("%H:%M")
        current_minute_key = now.strftime("%Y-%m-%d %H:%M")

        if (current_hm in self.WATERING_SCHEDULE
                and current_minute_key != self.last_scheduled_watering):
            self.last_scheduled_watering = current_minute_key
            if not self.controller.pump.is_active:
                self.controller.pump.turn_on()
                self.controller.db.log_event(
                    f"Насос ВКЛЮЧЁН по расписанию ({current_hm})"
                )

    # ──────────────────────────────────────────
    # Главный цикл
    # ──────────────────────────────────────────

    def _update(self):
        """
        Главный цикл обновления.
        Вызывается каждые UPDATE_INTERVAL миллисекунд через root.after().
        """
        self.controller.control()  # Читаем датчики и управляем
        self._check_schedule()      # Проверяем расписание
        self._refresh_sensors()     # Обновляем дисплей датчиков
        self._refresh_actuators()   # Обновляем статусы устройств
        self._refresh_log()         # Обновляем журнал

        self.status_var.set(
            f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}  |  "
            f"Следующее через 3 сек..."
        )
        # Планируем следующий вызов через 3 секунды
        # noinspection PyArgumentList
        self.root.after(self.UPDATE_INTERVAL, self._update)

    def run(self):
        """Запускает приложение."""
        self._update()          # Первый запуск
        self.root.mainloop()    # Передаём управление tkinter
