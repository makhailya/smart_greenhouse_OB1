import os
import sqlite3
import tempfile
from greenhouse.database import Database


class TestDatabaseInit:
    def test_creates_tables(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            Database(db_path)
            conn = sqlite3.connect(db_path)
            tables = [
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master"
                    " WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                    " ORDER BY name"
                )
            ]
            assert tables == ["events", "sensor_logs"]
        finally:
            os.unlink(db_path)


class TestDatabaseSensors:
    def test_log_sensors_succeeds(self, db):
        db.log_sensors(45.0, 22.5, 500)

    def test_log_and_read_sensors(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            db = Database(db_path)
            db.log_sensors(45.0, 22.5, 500)
            conn = sqlite3.connect(db_path)
            row = conn.execute(
                "SELECT humidity, temperature, light FROM sensor_logs"
            ).fetchone()
            assert row == (45.0, 22.5, 500)
        finally:
            os.unlink(db_path)


class TestDatabaseEvents:
    def test_log_event_and_get_recent(self, db):
        db.log_event("test event")
        events = db.get_recent_events()
        assert len(events) == 1
        assert events[0][1] == "test event"

    def test_get_recent_limit(self, db):
        for i in range(5):
            db.log_event(f"event {i}")
        events = db.get_recent_events(limit=3)
        assert len(events) == 3

    def test_get_recent_empty(self, db):
        assert db.get_recent_events() == []

    def test_events_ordered_by_id_desc(self, db):
        db.log_event("first")
        db.log_event("second")
        db.log_event("third")
        events = db.get_recent_events(10)
        assert [e[1] for e in events] == ["third", "second", "first"]
