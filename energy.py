#!/usr/bin/env python3
"""Energy monitor display for Four Letter pHAT."""

from flp_base import FlpMqttDisplay


class EnergyDisplay(FlpMqttDisplay):
    """Display energy data from Rainforest EAGLE monitor."""

    SUBSCRIPTIONS = [
        "rainforest/load",
        "rainforest/hourly",
        "rainforest/24h_compare",
        "rainforest/daily",
        "rainforest/peak",
    ]

    def get_subscriptions(self):
        return self.SUBSCRIPTIONS

    def get_required_topic(self):
        return "rainforest/load"

    @staticmethod
    def format_kw(value):
        """Format kW value for 4-char display (4 digits + decimal point)."""
        if value < 0:
            # Negative: minus sign takes 1 char, leaving 3 chars for digits
            abs_value = abs(value)
            if abs_value < 10:
                return f"{value:.2f}"  # -X.XX (e.g., -0.04, -9.99)
            elif abs_value < 100:
                return f"{value:.1f}"  # -XX.X (e.g., -10.5, -99.9)
            return f"{int(value)}"  # -XXX (e.g., -100, -999)
        else:
            # Positive: full 4 chars available for digits
            if value < 10:
                return f"{value:.3f}"
            elif value < 100:
                return f"{value:.2f}"
            return f"{int(value)}"

    def display_loop_iteration(self):
        """Display energy metrics cycle."""
        load = self.mqtt_data['rainforest/load']['instantaneous']

        # Current load
        self.display_message(['LOAD'], [self.format_kw(load)])

        # Hourly average (if available)
        if 'rainforest/hourly' in self.mqtt_data:
            hourly = self.mqtt_data['rainforest/hourly']['avg_kw']
            self.display_message(['1H'], [self.format_kw(hourly)])

        # Show current load again
        self.display_message([], [self.format_kw(load)])

        # 24h comparison (if available)
        if 'rainforest/24h_compare' in self.mqtt_data:
            diff = self.mqtt_data['rainforest/24h_compare']['diff_kw']
            self.display_message(['24H'], [self.format_kw(diff)])

        # Show current load again
        self.display_message([], [self.format_kw(load)])

        # Daily total (if available)
        if 'rainforest/daily' in self.mqtt_data:
            daily = self.mqtt_data['rainforest/daily']['total_kwh']
            self.display_message(['DAY'], [self.format_kw(daily)])

        # Show current load again
        self.display_message([], [self.format_kw(load)])

        # Peak usage today (if available)
        if 'rainforest/peak' in self.mqtt_data:
            peak = self.mqtt_data['rainforest/peak']['peak_kw']
            self.display_message(['PEAK'], [self.format_kw(peak)])

        # Show current load again
        self.display_message([], [self.format_kw(load)])


if __name__ == '__main__':
    display = EnergyDisplay()
    display.run()
