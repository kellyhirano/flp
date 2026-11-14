# Repository Guidelines

This file provides guidance to AI coding agents working with code in this repository. It is the canonical instruction file for this directory.

Display scripts for Pimoroni Four Letter pHAT on Raspberry Pi. Subscribe to MQTT topics and cycle through sensor values on a 4-character LED display.

## Project Structure & Module Organization

- `flp_base.py`: base class with MQTT setup, active-hours logic, and display helpers.
- `weather.py` / `energy.py`: concrete displays with topic subscriptions and display loops.
- `etc/systemd/system/`: systemd unit files for auto-start.
- `requirements.txt`: runtime dependencies.

## Build, Test, and Development Commands

- Install OS deps (on Raspberry Pi): `sudo apt-get install -y $(cat apt.txt)`.
- Install Python deps (venv): `python3 -m venv --system-site-packages venv && venv/bin/pip install -r requirements.txt`.
- Run directly: `python3 weather.py` or `python3 energy.py`.
- Enable service: `sudo cp etc/systemd/system/flp-weather.service /etc/systemd/system/` and `sudo systemctl enable --now flp-weather`.
- Ansible deploy (from controller): `ansible-playbook -i /home/hirano/dev/ansible/inventory/pis /home/hirano/dev/ansible/playbooks/flp-deploy.yml --ask-vault-pass`.

## Coding Style & Naming Conventions

- Python 3, 4-space indentation, snake_case for functions/modules, PascalCase for classes.
- Keep display logic in `display_loop_iteration()` implementations and MQTT topics in `get_subscriptions()`.
- Config file is `mqtt.conf` (INI format) in repo root.

## Architecture

The codebase uses a template method pattern:

- `FlpMqttDisplay` (flp_base.py) - Abstract base class providing:
  - MQTT connection setup and message handling
  - Display utilities (`display_message()`, `show_night_pattern()`)
  - Active hours logic (6:30 AM - 10:30 PM display, blinky pattern overnight)
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

| Mode | Topic | Purpose |
| --- | --- | --- |
| Weather | `weewx/sensor` | Temperature, wind, rain (required). |
| Weather | `purpleair/sensor` | AQI values. |
| Weather | `purpleair/last_hour` | AQI delta. |
| Energy | `rainforest/load` | Instantaneous kW (required). |
| Energy | `rainforest/hourly` | 60-minute average kW. |
| Energy | `rainforest/24h_compare` | Current vs 24h-ago. |
| Energy | `rainforest/daily` | Daily kWh total. |
| Energy | `rainforest/peak` | Peak kW today. |

## Testing Guidelines

- No automated tests; validate on real hardware.
- Manual checks: verify MQTT subscriptions, active-hours behavior (6:30 AM–10:30 PM), and display cycling.

## Commit & Pull Request Guidelines

- Use short, imperative commit summaries (e.g., “Add energy service”, “Refactor display loop”).
- PRs should list affected display modes, MQTT topics, and how you validated (commands + device used).
- If UI changes are visible, include a photo or short description of the display output.

## Configuration & Ops Notes

- Requires `mqtt.conf` in the project root (not tracked):
```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```
- Document new keys in `README.md`.
- Systemd units assume deployment on Raspberry Pi; update paths if installing elsewhere. Copy to `/etc/systemd/system/` and enable with systemctl.
- `apt.txt` includes `python3-smbus` (required for I2C hardware access); the venv must include system packages (`--system-site-packages`) to see `smbus`.
- On Raspberry Pi OS kernel `6.18.60+rpt` (introducing change not identified), zero-length I2C block writes fail with `EINVAL`; `fourletterphat` 0.1.0 uses them for HT16K33 commands. `flp_base.py` wraps `flp.bus` (`_I2CBusCompat`) to send them as `write_byte`. Don't remove it (outage 2026-11-12/13: every FLP service crash-looped after the kernel update).
- Freshness: the required topic must have arrived within `STALE_AFTER_SECS` (20 min weather, 5 min energy) or the display shows the waiting pattern and the Uptime Kuma heartbeat stops. Both required topics are retained on the broker, so after a restart/reconnect an old retained message counts as fresh for one window.
