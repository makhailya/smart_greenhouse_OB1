from unittest.mock import Mock, patch


class TestControllerInit:
    def test_loads_thresholds(self, controller):
        assert controller.thresholds == {
            "humidity_min": 40,
            "temperature_max": 30,
            "light_min": 300,
        }

    def test_creates_devices(self, controller):
        assert controller.humidity_sensor is not None
        assert controller.temperature_sensor is not None
        assert controller.light_sensor is not None
        assert controller.pump is not None
        assert controller.window is not None
        assert controller.lamp is not None


class TestControllerReadSensors:
    def test_updates_values(self, controller):
        controller.humidity_sensor.read = Mock(return_value=55.0)
        controller.temperature_sensor.read = Mock(return_value=24.0)
        controller.light_sensor.read = Mock(return_value=450)

        controller.read_sensors()

        assert controller.humidity == 55.0
        assert controller.temperature == 24.0
        assert controller.light == 450

    def test_logs_to_database(self, controller):
        controller.humidity_sensor.read = Mock(return_value=55.0)
        controller.temperature_sensor.read = Mock(return_value=24.0)
        controller.light_sensor.read = Mock(return_value=450)

        with patch.object(controller.db, "log_sensors") as mock_log:
            controller.read_sensors()
            mock_log.assert_called_once_with(55.0, 24.0, 450)


class TestControllerWatering:
    def test_activates_when_below_threshold(self, controller):
        controller.humidity = 30.0
        assert not controller.pump.is_active

        controller._control_watering()

        assert controller.pump.is_active

    def test_deactivates_when_above_threshold(self, controller):
        controller.pump.turn_on()
        controller.humidity = 50.0
        assert controller.pump.is_active

        controller._control_watering()

        assert not controller.pump.is_active

    def test_noop_when_already_correct(self, controller):
        controller.humidity = 50.0
        controller.pump.turn_off()
        before = len(controller.db.get_recent_events(100))

        controller._control_watering()

        assert not controller.pump.is_active
        assert len(controller.db.get_recent_events(100)) == before


class TestControllerVentilation:
    def test_activates_when_above_threshold(self, controller):
        controller.temperature = 35.0
        assert not controller.window.is_active

        controller._control_ventilation()

        assert controller.window.is_active

    def test_deactivates_when_below_threshold(self, controller):
        controller.window.turn_on()
        controller.temperature = 25.0
        assert controller.window.is_active

        controller._control_ventilation()

        assert not controller.window.is_active

    def test_noop_when_already_correct(self, controller):
        controller.temperature = 25.0
        controller.window.turn_off()
        before = len(controller.db.get_recent_events(100))

        controller._control_ventilation()

        assert not controller.window.is_active
        assert len(controller.db.get_recent_events(100)) == before


class TestControllerLighting:
    def test_activates_when_below_threshold(self, controller):
        controller.light = 200
        assert not controller.lamp.is_active

        controller._control_lighting()

        assert controller.lamp.is_active

    def test_deactivates_when_above_threshold(self, controller):
        controller.lamp.turn_on()
        controller.light = 500
        assert controller.lamp.is_active

        controller._control_lighting()

        assert not controller.lamp.is_active

    def test_noop_when_already_correct(self, controller):
        controller.light = 500
        controller.lamp.turn_off()
        before = len(controller.db.get_recent_events(100))

        controller._control_lighting()

        assert not controller.lamp.is_active
        assert len(controller.db.get_recent_events(100)) == before


class TestControllerControlLoop:
    def test_orchestrates_read_and_control_methods(self, controller):
        controller.humidity_sensor.read = Mock(return_value=30.0)
        controller.temperature_sensor.read = Mock(return_value=35.0)
        controller.light_sensor.read = Mock(return_value=200)

        with (
            patch.object(controller, "read_sensors") as mock_read,
            patch.object(controller, "_control_watering") as mock_water,
            patch.object(controller, "_control_ventilation") as mock_vent,
            patch.object(controller, "_control_lighting") as mock_light,
        ):
            controller.control()
            mock_read.assert_called_once()
            mock_water.assert_called_once()
            mock_vent.assert_called_once()
            mock_light.assert_called_once()

    def test_logs_events_via_db(self, controller):
        controller.humidity_sensor.read = Mock(return_value=30.0)
        controller.temperature_sensor.read = Mock(return_value=35.0)
        controller.light_sensor.read = Mock(return_value=200)

        controller.control()

        events = controller.db.get_recent_events(10)
        assert len(events) == 3
        event_texts = [e[1] for e in events]
        assert any("Насос ВКЛЮЧЁН" in e for e in event_texts)
        assert any("Окно ОТКРЫТО" in e for e in event_texts)
        assert any("Лампа ВКЛЮЧЕНА" in e for e in event_texts)
