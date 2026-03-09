#!/usr/bin/env python3
"""Base class for Four Letter pHAT MQTT display scripts."""

import configparser
import json
import time
from abc import ABC, abstractmethod

import paho.mqtt.client as mqtt
import fourletterphat as flp


class FlpMqttDisplay(ABC):
    """Base class for FLP displays that subscribe to MQTT topics."""

    # Active display hours (7 AM to 11 PM)
    ACTIVE_START_HOUR = 7
    ACTIVE_END_HOUR = 23

    # Reconnection settings
    RECONNECT_DELAY_SECS = 5
    MAX_RECONNECT_DELAY_SECS = 300

    def __init__(self, config_file='mqtt.conf'):
        self.mqtt_data = {}
        self.client = None
        self._connected = False
        self._reconnect_delay = self.RECONNECT_DELAY_SECS
        self._load_config(config_file)
        self._setup_mqtt()

    def _load_config(self, config_file):
        """Load MQTT configuration from file."""
        config = configparser.ConfigParser()
        config.read(config_file)
        self.mqtt_host = config.get('ALL', 'mqtt_host')
        self.mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

    def _setup_mqtt(self):
        """Set up MQTT client with callbacks."""
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK from the server."""
        if rc == 0:
            print("Connected to MQTT broker")
            self._connected = True
            self._reconnect_delay = self.RECONNECT_DELAY_SECS  # Reset delay on success
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe([(topic, 0) for topic in self.get_subscriptions()])
        else:
            print(f"Connection failed with code {rc}")
            self._connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server."""
        self._connected = False
        if rc != 0:
            print(f"Unexpected disconnection (rc={rc}). Will auto-reconnect...")
        else:
            print("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server."""
        print(msg.topic + " -> " + str(msg.payload.decode('UTF-8')))
        message_data = json.loads(str(msg.payload.decode('UTF-8')))
        self.mqtt_data[msg.topic] = message_data
        self._flash_decimal()

    def _flash_decimal(self):
        """Flash the rightmost decimal to show receipt of a message."""
        flp.set_decimal(3, True)
        flp.show()
        time.sleep(.5)
        flp.set_decimal(3, False)
        flp.show()
        time.sleep(.25)
        flp.set_decimal(3, True)
        flp.show()
        time.sleep(.5)
        flp.set_decimal(3, False)
        flp.show()

    @staticmethod
    def display_message(titles, numbers, show_title_at_end=False,
                        number_sleep=1, title_sleep=.5):
        """Display messages with different timings for titles vs numbers."""
        for title in titles:
            flp.clear()
            flp.print_str(title)
            flp.show()
            time.sleep(title_sleep)

        for number in numbers:
            flp.clear()
            flp.print_number_str(str(number))
            flp.show()
            time.sleep(number_sleep)

        if show_title_at_end:
            for title in titles:
                flp.clear()
                flp.print_str(title)
                flp.show()
                time.sleep(title_sleep)

    @staticmethod
    def show_night_pattern():
        """Show a blinky pattern for night mode."""
        flp.clear()
        for i in range(4):
            flp.set_decimal(i, True)
            flp.show()
            time.sleep(.1)
            flp.set_decimal(i, False)
            flp.show()
        time.sleep(8)  # Total ~10s of sleep

    @staticmethod
    def is_active_hours():
        """Check if current time is within active display hours."""
        current_hour = int(time.strftime("%H", time.localtime()))
        return FlpMqttDisplay.ACTIVE_START_HOUR <= current_hour <= FlpMqttDisplay.ACTIVE_END_HOUR

    def has_required_data(self):
        """Check if the required MQTT topic has data."""
        return self.get_required_topic() in self.mqtt_data

    @abstractmethod
    def get_subscriptions(self):
        """Return list of MQTT topics to subscribe to."""
        pass

    @abstractmethod
    def get_required_topic(self):
        """Return the topic that must have data before display starts."""
        pass

    @abstractmethod
    def display_loop_iteration(self):
        """Perform one iteration of the display loop during active hours."""
        pass

    def run(self):
        """Main run loop."""
        self.client.connect_async(self.mqtt_host, self.mqtt_host_port, 60)
        self.client.loop_start()

        while True:
            # Check connection status and show indicator if disconnected
            if not self._connected:
                self._show_disconnected()
                time.sleep(5)
                continue

            if not self.has_required_data():
                self._show_waiting()
                time.sleep(5)
                continue

            try:
                if self.is_active_hours():
                    self.display_loop_iteration()
                else:
                    self.show_night_pattern()
            except Exception as e:
                print(f"Display error: {e}")
                self._show_error()

            time.sleep(2)

    def _show_disconnected(self):
        """Show disconnection indicator on display."""
        flp.clear()
        flp.print_str("DISC")
        flp.show()

    def _show_waiting(self):
        """Show waiting indicator on display."""
        flp.clear()
        flp.print_str("WAIT")
        flp.show()

    def _show_error(self):
        """Show error indicator on display."""
        flp.clear()
        flp.print_str("ERR")
        flp.show()
        time.sleep(2)
