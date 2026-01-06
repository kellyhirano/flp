# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Display scripts for Pimoroni Four Letter pHAT on Raspberry Pi. Subscribe to MQTT topics and cycle through sensor values on a 4-character LED display.

## Running Scripts

```bash
# Install dependencies (on Raspberry Pi)
sudo apt-get install -y $(cat apt.txt)
python3 -m venv --system-site-packages venv
venv/bin/pip install -r requirements.txt

# Run directly
python3 weather.py
python3 energy.py
```

## Deployment

For production deployment to Raspberry Pi hosts:
```bash
# From Ansible controller
ansible-playbook -i /home/hirano/dev/ansible/inventory/pis \
  /home/hirano/dev/ansible/playbooks/flp-deploy.yml --ask-vault-pass
```

## Configuration

Requires `mqtt.conf` in the project root:
```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```

## Architecture

The codebase uses a template method pattern:

- `FlpMqttDisplay` (flp_base.py) - Abstract base class providing:
  - MQTT connection setup and message handling
  - Display utilities (`display_message()`, `show_night_pattern()`)
  - Active hours logic (7 AM - 11 PM display, blinky pattern overnight)
  - Main run loop with `loop_start()` for async MQTT

- Subclasses implement three abstract methods:
  - `get_subscriptions()` - List of MQTT topics to subscribe to
  - `get_required_topic()` - Topic that must have data before display starts
  - `display_loop_iteration()` - One cycle of the display routine

### Display Constraints

The Four Letter pHAT has a 4-character LED display (decimals can appear after any character without consuming additional positions). When formatting numbers:

- **Positive values**: Use all 4 characters (e.g., `1.234`, `12.34`, `123.4`, `1234`)
- **Negative values**: Minus sign takes 1 character, leaving 3 for digits (e.g., `-0.04`, `-10.5`, `-100`)

The `format_kw()` helper in `energy.py` handles this automatically, adjusting decimal precision based on value magnitude and sign.

## MQTT Topics

**Weather display** (`weather.py`):
- `weewx/sensor` (required) - Temperature, wind, rain from WeeWX
- `purpleair/sensor` - EPA AQI data
- `purpleair/last_hour` - AQI change over last hour

**Energy display** (`energy.py`):
- `rainforest/load` (required) - Instantaneous kW demand
- `rainforest/hourly` - 60-min average kW
- `rainforest/24h_compare` - Current vs 24h-ago comparison
- `rainforest/daily` - Daily kWh total
- `rainforest/peak` - Peak kW today

## Systemd Services

Service files in `etc/systemd/system/` for running on boot. Copy to `/etc/systemd/system/` and enable with systemctl.

## Dependencies

- `apt.txt` - OS-level packages including `python3-smbus` (required for I2C hardware access)
- `requirements.txt` - Python packages installed in venv with `--system-site-packages` to access smbus
