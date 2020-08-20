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


config = configparser.ConfigParser()
config.read('mqtt.conf')

mqtt_host = config.get('ALL', 'mqtt_host')
mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, mqtt_host_port, 60)


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
    if ('purpleair/sensor' in g_mqtt_data):
        aqi = g_mqtt_data['purpleair/sensor']['st_aqi']

    current_hour = int(time.strftime("%H", time.localtime()))
    if (current_hour >= 7 and current_hour <= 23):

        if (aqi >= 100):
            print('AQI: {}'.format(aqi))
            flp.clear()
            flp.print_str('AWI')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_number_str(aqi)
            flp.show()
            time.sleep(2)

        if (wind_gust >= 10):
            print('GUST: {}'.format(wind_gust))
            flp.clear()
            flp.print_str('GUST')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_number_str(wind_gust)
            flp.show()
            time.sleep(2)

        if (rain_rate > 0):
            print('RAIN: {:.2f}h'.format(rain_rate))
            flp.clear()
            flp.print_str('RAIN')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_str('RATE')
            flp.show()
            time.sleep(.5)
            flp.clear()
            flp.print_float(rain_rate, decimal_digits=2)
            flp.show()
            time.sleep(2)

        flp.clear()
        flp.print_str('TEMP')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(temp, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_float(temp_change, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_float(temp, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_str('24H')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(temp_change_24h, decimal_digits=1)
        flp.show()
        time.sleep(2)
        flp.clear()
        flp.print_str('24H')
        flp.show()
        time.sleep(.5)
        flp.clear()
        flp.print_float(temp, decimal_digits=1)
        flp.show()

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
