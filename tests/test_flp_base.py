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
