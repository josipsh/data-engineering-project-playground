# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A mock data engineering playground that generates realistic environmental sensor data from fictional ocean-deployed devices. The goal of **this repo** is solely the CLI that generates mock data — the downstream pipelines are out of scope.

The data flows: CLI generates binary-encoded sensor payloads → written to NDJSON/CSV/XML/Avro (or pushed to Kafka/RabbitMQ/S3).

## Setup & Commands

This project uses `uv` for Python dependency management (Python 3.11+ required).

```bash
# Install dependencies
uv sync

# Run the CLI
uv run python main.py --config configs/sample.yaml

# Override individual config values via flags
uv run python main.py --config configs/sample.yaml --output-format avro --number-of-fleets 3
```

No tests or linting tools are configured yet.

## Architecture

The project is pre-implementation. The spec lives in `README.md`. Key design decisions to carry through:

### CLI (`main.py`)
Supports a config file with CLI overrides. Parameters:
- `output-format` — `json`, `json-with-binary-payload`, `xml`, `xml-with-binary-payload`, `csv`, `csv-with-binary-payload`, `avro`, `avro-with-binary-payload`
- `output-type` — `kafka-only`, `rabbitmq-only`, `s3-only`, `s3-with-kafka`, `s3-with-rabbitmq`
- `number-of-devices-per-fleet` — integer
- `number-of-fleets` — integer
- `dimensions` — `all` or a list of dimension strings from the 10 measurable dimensions
- `rate-of-emitting-dp` — `1-per-second`, `10-per-second`, `1-per-minute`, `10-per-minute`, `1-per-hour`, `10-per-hour`
- `error-rate` — `none`, `low`, `medium`, `high`, `critical`, `certain`

### Device Model
Devices are deployed in fleets of 100 in a 20 m × 20 m grid. Each fleet has a "flagship" device that relays data via RF. Devices have: solar panel, battery, computer, antenna/RF, and sensors. Multiple hardware generations and firmware versions exist — newer generations measure more datapoints.

### Measurable Dimensions (10)
Temperature, Humidity, CO₂, Ozone, Nitrogen Dioxide, Barometric Pressure, Solar Radiation, Salinity, pH, Plastics.

### Binary Payload Format (WIP per README)
Big-endian. Approximate layout:
- 1 B: format version
- 1 B: firmware version
- 1 B: device ID
- 1 B: battery level
- 1 B: CPU utilization
- 1 B: CPU temperature
- variable: data section — one record per datapoint, repeated per dimension
- 1 B: number of datapoints
- 1 B: checksum (CRC)

## Development Rules

- Implement component by component — one component at a time, not all at once.
- Every design decision must be confirmed before any implementation begins.
- Do not add any package or dependency without explicit user confirmation.
- Every piece of code must be testable. Design interfaces (e.g. dependency injection, ABCs/protocols) so tests can be written without monkey-patching. If monkey-patching is unavoidable, flag it to the user before proceeding.
- Use `uv` for all package management (`uv add`, `uv sync`).
- For running scripts use exclusively `UV`, no `pip`, no `python -m <script-file>`, etc
- Prefer YAML over JSON for all config files.