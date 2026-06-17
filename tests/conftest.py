import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from greenhouse.database import Database

MOCK_CONFIG = {
    "thresholds": {"humidity_min": 40, "temperature_max": 30, "light_min": 300},
    "schedule": {"watering_times": ["08:00", "12:00", "18:00"]},
}


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        yield Database(db_path)
    finally:
        os.unlink(db_path)


@pytest.fixture
def controller():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        db = Database(db_path)
        with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
            with patch("greenhouse.controller.Database", return_value=db):
                from greenhouse.controller import GreenhouseController
                ctrl = GreenhouseController()
                yield ctrl
    finally:
        os.unlink(db_path)
