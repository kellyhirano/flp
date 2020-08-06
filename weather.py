#!/usr/bin/env python3

import configparser
import json
import time
import paho.mqtt.client as mqtt
import fourletterphat as flp

# Global for data storage
g_outside_temp = 0
g_outside_temp_change = 0
g_outside_24h_temp_change = 0
g_last_day_rain = 0
g_rain_rate = 0
g_wind_gust = 0


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK from the server."""
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([("weewx/sensor", 0),
                      ("awair/Family Room/sensor", 0),
                      ("awair/Master Bedroom/sensor", 0),
                      ("awair/Living Room/sensor", 0)])


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global g_outside_temp
    global g_outside_temp_change
    global g_outside_24h_temp_change
    global g_last_day_rain
    global g_rain_rate
    global g_wind_gust

    print(msg.topic+" -> "+str(msg.payload.decode('UTF-8')))
    weather_data = json.loads(str(msg.payload.decode('UTF-8')))

    g_outside_temp = weather_data['outdoor_temperature']
    g_outside_temp_change = weather_data['outdoor_temp_change']
    g_outside_24h_temp_change = weather_data['outdoor_24h_temp_change']
    g_last_day_rain = weather_data['last_day_rain']
    g_rain_rate = weather_data['rain_rate']
    g_wind_gust = weather_data['wind_gust']

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


config = configparser.ConfigParser()
config.read('mqtt.conf')

mqtt_host = config.get('ALL', 'mqtt_host')
mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, mqtt_host_port, 60)

while(1):
    current_hour = int(time.strftime("%H", time.localtime()))

    if (current_hour >= 7 and current_hour <= 23 and g_outside_temp):

        if (g_wind_gust >= 10):
            print('GUST: {}'.format(g_wind_gust))
            flp.clear()
            flp.print_str('GUST')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_number_str(g_wind_gust)
            flp.show()
            time.sleep(2)

        if (g_rain_rate):
            print('RAIN: {:.2f}h'.format(g_rain_rate))
            flp.clear()
            flp.print_str('RAIN')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_str('RATE')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_float(g_rain_rate, decimal_digits=2)
            flp.show()
            time.sleep(2)

        flp.clear()
        flp.print_str('TEMP')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(g_outside_temp, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_float(g_outside_temp_change, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_float(g_outside_temp, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_str('24H')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(g_outside_24h_temp_change, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_str('24H')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(g_outside_temp, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()

    # Give the main display a rest at night and show a blinky pattern
    else:
        flp.clear()
        for i in range(4):
            flp.set_decimal(i, True)
            flp.show()
            time.sleep(.1)
            flp.set_decimal(i, False)
            flp.show()
        time.sleep(5)

    client.loop()
    time.sleep(5)
