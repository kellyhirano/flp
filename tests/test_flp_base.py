import time
from unittest.mock import patch
from flp_base import FlpMqttDisplay


class TestIsActiveHours:
    def test_midday_is_active(self):
        with patch('time.localtime',
                   return_value=time.struct_time((2026, 4, 12, 12, 0, 0, 0, 0, -1))):
            assert FlpMqttDisplay.is_active_hours() is True

    def test_start_boundary_active(self):
        with patch('time.localtime',
                   return_value=time.struct_time((2026, 4, 12, 6, 30, 0, 0, 0, -1))):
            assert FlpMqttDisplay.is_active_hours() is True

    def test_end_boundary_active(self):
        with patch('time.localtime',
                   return_value=time.struct_time((2026, 4, 12, 22, 29, 0, 0, 0, -1))):
            assert FlpMqttDisplay.is_active_hours() is True

    def test_just_before_start_inactive(self):
        with patch('time.localtime',
                   return_value=time.struct_time((2026, 4, 12, 6, 29, 0, 0, 0, -1))):
            assert FlpMqttDisplay.is_active_hours() is False

    def test_midnight_inactive(self):
        with patch('time.localtime',
                   return_value=time.struct_time((2026, 4, 12, 0, 0, 0, 0, 0, -1))):
            assert FlpMqttDisplay.is_active_hours() is False


class _Display(FlpMqttDisplay):
    def __init__(self):
        self.mqtt_data = {}
        self._received_at = {}

    def get_subscriptions(self):
        return ['t']

    def get_required_topic(self):
        return 't'

    def display_loop_iteration(self):
        pass


class TestHasRequiredData:
    def test_missing(self):
        assert _Display().has_required_data() is False

    def test_fresh(self):
        d = _Display()
        d._received_at['t'] = time.monotonic()
        assert d.has_required_data() is True

    def test_stale(self):
        d = _Display()
        d._received_at['t'] = time.monotonic() - d.STALE_AFTER_SECS - 1
        assert d.has_required_data() is False
