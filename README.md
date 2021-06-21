# flp
A script designed to display weather information on a [Pimoroni Four Letter
pHAT](https://shop.pimoroni.com/products/four-letter-phat). It's reading data from my local mqtt server that's using specific topic names. I need to clean up that code and will link to that as well.

A mqtt.conf file must be created. It's a standard configparser doc that must define a MQTT server and it's port (default port is 1883).
```
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
```

### Running automatically on boot

```
sudo cp etc/systemd/system/flp-weather.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flp-weather
sudo systemctl start flp-weather
```
