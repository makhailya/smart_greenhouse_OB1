import sqlite3
from datetime import datetime


class Database:
    """Управляет сохранением данных в SQLite."""

    def __init__(self, db_path: str = "greenhouse.db"):
        self.db_path = db_path
        self._create_tables()  # Создаём таблицы при старте

    def _create_tables(self):
        """Создаёт таблицы, если их ещё нет."""
        with sqlite3.connect(self.db_path) as conn:
            # Таблица для показаний датчиков
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT    NOT NULL,
                    humidity  REAL,
                    temperature REAL,
                    light     INTEGER
                )
            """)
            # Таблица для событий (насос вкл/выкл и т.д.)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event     TEXT NOT NULL
                )
            """)

    def log_sensors(self, humidity: float, temperature: float, light: int):
        """Записывает показания датчиков в БД."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO sensor_logs (timestamp, humidity, temperature, light) "
                "VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), humidity, temperature, light)
            )

    def log_event(self, event: str):
        """Записывает событие (например, 'Насос включён')."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (timestamp, event) VALUES (?, ?)",
                (datetime.now().isoformat(), event)
            )

    def get_recent_events(self, limit: int = 20) -> list:
        """Возвращает последние N событий для отображения в GUI."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, event FROM events ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        