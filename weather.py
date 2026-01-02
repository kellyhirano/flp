#!/usr/bin/env python3
"""Weather and AQI display for Four Letter pHAT."""

from flp_base import FlpMqttDisplay


class WeatherDisplay(FlpMqttDisplay):
    """Display weather and air quality data."""

    SUBSCRIPTIONS = [
        "weewx/sensor",
        "purpleair/sensor",
        "purpleair/last_hour",
    ]

    def get_subscriptions(self):
        return self.SUBSCRIPTIONS

    def get_required_topic(self):
        return "weewx/sensor"

    def display_loop_iteration(self):
        """Display weather metrics cycle."""
        weewx = self.mqtt_data['weewx/sensor']
        temp = weewx['outdoor_temperature']
        temp_change = weewx['outdoor_temp_change']
        temp_change_24h = weewx['outdoor_24h_temp_change']
        rain_rate = weewx['rain_rate']
        wind_gust = weewx['wind_gust']

        aqi = 0
        last_1hr_aqi = 0
        if 'purpleair/sensor' in self.mqtt_data:
            aqi = self.mqtt_data['purpleair/sensor']['st_aqi']

        if 'purpleair/last_hour' in self.mqtt_data:
            last_1hr_aqi = self.mqtt_data['purpleair/last_hour']['st_aqi']

        if aqi >= 100:
            self.display_message(['AQI'], [aqi, last_1hr_aqi])

        if wind_gust >= 10:
            self.display_message(['GUST'], [wind_gust])

        if rain_rate > 0:
            self.display_message(['RAIN', 'RATE'], [rain_rate])

        self.display_message(['TEMP'], [temp])

        self.display_message(['1H'], [temp_change])

        self.display_message([], [temp])

        self.display_message(['24H'], [temp_change_24h])

        self.display_message([], [temp])


if __name__ == '__main__':
    display = WeatherDisplay()
    display.run()
