#!/usr/bin/env python3

import configparser
import json
import time
import paho.mqtt.client as mqtt
import fourletterphat as flp

# Global for data storage
g_mqtt_data = {}


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK from the server."""
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([("weewx/sensor", 0),
                      ("purpleair/sensor", 0),
                      ("purpleair/last_hour", 0),
                      ("awair/Family Room/sensor", 0),
                      ("awair/Master Bedroom/sensor", 0),
                      ("awair/Living Room/sensor", 0)])


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global g_mqtt_data

    print(msg.topic+" -> "+str(msg.payload.decode('UTF-8')))
    message_data = json.loads(str(msg.payload.decode('UTF-8')))

    g_mqtt_data[msg.topic] = message_data

    # Flash the rightmost decimal to show receipt of a message
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


def display_message(titles, numbers, show_title_at_end=False,
                    number_type='str', float_decimal_digits=1,
                    number_sleep=1, title_sleep=.5):
    """Display messaages with different timings for titles vs numbers."""

    for title in titles:
        flp.print_str(title)
        flp.show()
        time.sleep(title_sleep)

    for number in numbers:
        if (number_type == 'str'):
            flp.print_number_str(number)
        elif (number_type == 'float'):
            flp.print_float(number, float_decimal_digits)
        flp.show()
        time.sleep(number_sleep)

    if (show_title_at_end):
        for title in titles:
            flp.print_str(title)
            flp.show()
            time.sleep(title_sleep)


config = configparser.ConfigParser()
config.read('mqtt.conf')

mqtt_host = config.get('ALL', 'mqtt_host')
mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect_async(mqtt_host, mqtt_host_port, 60)
client.loop_start()

while(1):
    if ('weewx/sensor' not in g_mqtt_data):
        time.sleep(5)
        client.loop()
        continue

    temp = g_mqtt_data['weewx/sensor']['outdoor_temperature']
    temp_change = g_mqtt_data['weewx/sensor']['outdoor_temp_change']
    temp_change_24h = g_mqtt_data['weewx/sensor']['outdoor_24h_temp_change']
    rain_rate = g_mqtt_data['weewx/sensor']['rain_rate']
    wind_gust = g_mqtt_data['weewx/sensor']['wind_gust']

    aqi = 0
    last_1hr_aqi = 0
    if ('purpleair/sensor' in g_mqtt_data):
        aqi = g_mqtt_data['purpleair/sensor']['st_aqi']

    if ('purpleair/last_hour' in g_mqtt_data):
        last_1hr_aqi = g_mqtt_data['purpleair/last_hour']['st_aqi']

    current_hour = int(time.strftime("%H", time.localtime()))
    if (current_hour >= 7 and current_hour <= 23):

        if (aqi >= 100):
            display_message(['AQI'], [aqi, last_1hr_aqi])

        if (wind_gust >= 10):
            display_message(['GUST'], [wind_gust])

        if (rain_rate > 0):
            display_message(['RAIN', 'RATE'], [rain_rate],
                            number_type='float', float_decimal_digits=2)

        display_message(['TEMP'], [temp],
                        number_type='float', number_sleep=2)

        display_message(['1H'], [temp_change],
                        number_type='float', show_title_at_end=True)

        display_message([], [temp], number_type='float', number_sleep=2)

        display_message(['24H'], [temp_change_24h],
                        number_type='float', show_title_at_end=True)

        display_message([], [temp], number_type='float', number_sleep=0)

    # Give the main display a rest at night and show a blinky pattern
    else:
        flp.clear()
        for i in range(4):
            flp.set_decimal(i, True)
            flp.show()
            time.sleep(.1)
            flp.set_decimal(i, False)
            flp.show()
        time.sleep(8) # Total = 10s of sleep

    time.sleep(2)
