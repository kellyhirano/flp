# flp
Scripts designed to display sensor information on a [Pimoroni Four Letter pHAT](https://shop.pimoroni.com/products/four-letter-phat). Data is read from a local MQTT server with specific topic names.

## Scripts

- **weather.py** - Displays weather and air quality data (temperature, AQI, wind, rain)
- **energy.py** - Displays energy consumption data from a [Rainforest EAGLE-3](https://www.rainforestautomation.com/rfa-z114-eagle-3/) energy monitor

## Setup

A `mqtt.conf` file must be created with MQTT server settings:
```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```

Install dependencies:
```
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
```

## Running automatically on boot

### Weather display
```
sudo cp etc/systemd/system/flp-weather.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flp-weather
sudo systemctl start flp-weather
```

### Energy display
```
sudo cp etc/systemd/system/flp-energy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flp-energy
sudo systemctl start flp-energy
```
