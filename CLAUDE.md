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
uv run python src/main.py --config configs/sample.yaml

# Override individual config values via flags
uv run python src/main.py --config configs/sample.yaml --output-format avro --number-of-fleets 3
```

No tests or linting tools are configured yet.

## Architecture

The project is pre-implementation. The spec lives in `README.md`. Key design decisions to carry through:

### CLI (`src/cli_generate.py` or similar)
Supports a config file with CLI overrides. Parameters:
- `output-format` — `json`, `json_with_binary_payload`, `xml`, `xml_with_binary_payload`, `csv`, `csv_with_binary_payload`, `avro`, `avro_with_binary_payload`
- `output-type` — `kafka`, `rabbitmq`, `s3_with_queue`, `s3`
- `number-of-dp` — datapoints per device per emission (integer)
- `number-of-devices-per-fleet` — integer
- `number-of-fleets` — integer
- `dimensions` — `all` or a comma-separated subset of the 14 measurable dimensions
- `rate-of-emitting-dp` — `<integer> per <second|minute|hour>`
- `error-rate` — `none` or per-component rate for injecting faults

### Device Model
Devices are deployed in fleets of 100 in a 20 m × 20 m grid. Each fleet has a "flagship" device that relays data via RF. Devices have: solar panel, battery, computer, antenna/RF, and sensors. Multiple hardware generations and firmware versions exist — newer generations measure more datapoints.

### Measurable Dimensions (14)
Temperature, Humidity, CO₂, Ozone, Nitrogen Dioxide, Barometric Pressure, Solar Radiation, Salinity, pH, Dissolved Oxygen, Turbidity, Electrical Conductivity, Metals, Plastics (by size range).

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
- Prefer YAML over JSON for all config files.