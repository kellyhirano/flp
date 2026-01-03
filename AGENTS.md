# Repository Guidelines

## Project Structure & Module Organization
This repository contains Python 3 display scripts for the Pimoroni Four Letter pHAT. Key files:

- `flp_base.py`: base class with MQTT setup, active-hours logic, and display helpers.
- `weather.py` / `energy.py`: concrete displays with topic subscriptions and display loops.
- `etc/systemd/system/`: systemd unit files for auto-start.
- `requirements.txt`: runtime dependencies.

## Build, Test, and Development Commands
- Install deps (on Raspberry Pi): `sudo pip3 install -r requirements.txt`.
- Run directly: `python3 weather.py` or `python3 energy.py`.
- Enable service: `sudo cp etc/systemd/system/flp-weather.service /etc/systemd/system/` and `sudo systemctl enable --now flp-weather`.

## Coding Style & Naming Conventions
- Python 3, 4-space indentation, snake_case for functions/modules, PascalCase for classes.
- Keep display logic in `display_loop_iteration()` implementations and MQTT topics in `get_subscriptions()`.
- Config file is `mqtt.conf` (INI format) in repo root.

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
- Manual checks: verify MQTT subscriptions, active-hours behavior (7 AM–11 PM), and display cycling.

## Commit & Pull Request Guidelines
- Use short, imperative commit summaries (e.g., “Add energy service”, “Refactor display loop”).
- PRs should list affected display modes, MQTT topics, and how you validated (commands + device used).
- If UI changes are visible, include a photo or short description of the display output.

## Configuration & Ops Notes
- `mqtt.conf` is required and not tracked; document new keys in `README.md`.
- Systemd units assume deployment on Raspberry Pi; update paths if installing elsewhere.
