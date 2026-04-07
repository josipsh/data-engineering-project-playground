# data-engineering-project-playground

The motivation behind this mock project is to have simple yet complicated enough project in which you can sharp the DE skills.
The idea, is to have a project in which you can practice:
- batch spark
- spark streaming
- traditional programming
- streaming/batch pipeline in non-spark technology
- etc
Also, idea is to have somewhat real world project in which you could compare different approaches and compare the dimension like cost, speed, complexity, etc

The device itself does not exist it is completely made up.

# Introduction
You are an data engineer who is tasked to design and implement the data pipeline which will process the data from the device that measures the environmental dimensions like temperature. More about the device itself we will dive in in the coming sections.

You have complete control of the technology stack as long as you are within the budget (that you set) and you delivered the deliverable (later will be explained).

# Device
The data is coming from the device that measures the environmental dimensions.
The device itself is the state of the art which can measure in vertical space.
The dimensions the device can measure are:
- Temperature
- humidity
- Co2
- Ozone
- Nitrogen Dioxide
- Sulfur Dioxide
- Barometric Pressure
- Solar Radiation
- Salinity
- pH
- Dissolved Oxygen
- Turbidity
- Electrical Conductivity
- Metals
- Amount of plastic that where the size is between xx and zz

We have an technology which can measure all dimensions mentioned above.
Also, some newer devices can measure then 10 meter horizontally/vertically/dept from the device itself.
Devices are deployed in the fleets of 100, in grid of 20m by 20m. In each fleet we have an flagship, which is the most powerful device that could emit storing enough signal so we can collect if wherever the fleet is in the pacific ocean.

Each device has the following components:
- Solar panel
- Battery
- Computer
- Antenna/RF components
- Measuring sensors

For each of these component we have data to measure the efficiency of said component.

Also, we have multiple generations of these devices as well as multiple firmware versions. The newer the generation, the more datapoint device can measure.

Since we use RF to transfer the data from flagship device to the could, the payload is design to be efficient as possible. Which means everything is in binary format.
The binary format specification for each firmware version you can [here](#Binary-format-specification).

# Backend
On the receiving end or collector side, we have setup simple backend that receives the data from RF channel and calculates the checksum of given data and pushes it to the queue.

# Requirements-of-pipeline
You job is to design and implement the pipeline that accommodates the following requirements:
- We want to know how many devices are malfunctioning. Malfunctioning could be one of the following:
	- Battery health is not good
	- Energy produced is not sufficient
	- No data is coming from device/fleet
	- Data loss is more that 40% (40% of data per device/fleet is missing)
- We want to be able to calculate the min/max/mean/median/ for each dimension over time (per day/month/year)
- Table should be modeled in such way that we can support various visualization (e.g. see on. the map where the fleet is, visualize each data point and ranges, etc)
- The access to this data should be done in such way that we can easily export it to the interested third party

# CLI for generating mock data
Like we said is before, nothing of this is real. So we have created an CLI which can generate the mock data.
Here are options that CLI supports:
- output-formats:
	- json
	- xml
	- csv
	- avro
- output-type:
	- Kafka
	- RabbitMq
	- S3 + some queue (to provide metadata of stored file)
    - only S3
- number-of-dp: basically how many datapoint we generate for each device
	- 1 dp per selected dimension
	- 5 dp per selected dimension
	- etc
- number-of-devices-per-fleet:
	- integer
- number-of-fleets
	- integer
- dimensions: for which data will be generated
	- all
	- list of selected
- rate-of-emitting-dp:
	- 1 per hour
	- 1 per minute
	- 1 per secund
	- 10 per secund
	- 100 per secund (maybe not needed)
    - <integer> per <time-window>
- error-rate:
	- no error
	- some rate per component


The CLI can be configure via config file and/or overridden by CLI parameters 

# Repo layout
The repository follows a simple layout to keep code, config, and outputs separated:
- `src/` holds implementation modules and CLI entry points
- `configs/` contains example and local configuration files
- `outputs/` is for locally generated data artifacts

Initial naming conventions:
- Python modules use `snake_case.py`
- Packages use lowercase names (e.g., `payload_encoder/`)
- CLI entry points use `cli_<feature>.py` or `main.py`
- Config files use `*.yaml`

# Development setup (uv)
This project uses the uv package manager.

Create a virtual environment and sync dependencies:
```bash
uv venv
uv sync
```

# CLI-usage
Generate mock data using the sample config:
```bash
python -m src.main --config configs/sample.yaml
```

Override values on the command line and enable validation:
```bash
python -m src.main --config configs/sample.yaml --output-format csv --number-of-fleets 2 --validate
```

# Binary-format-specification
We use a compact binary payload with scaled integers (happy path). This specification is versioned and big-endian.

Rules
- All multi-byte fields are big-endian.
- Signed fields use two's complement.
- Scaling: `raw = round(value / scale)`, `value = raw * scale`.
- CRC-16-CCITT-FALSE over all bytes before CRC, appended as 2 bytes big-endian.
  - poly `0x1021`, init `0xFFFF`, xorout `0x0000`, refin `false`, refout `false`.

Header fields (fixed section)

| Offset | Size (bytes) | Field | Type | Scale/Unit |
| --- | --- | --- | --- | --- |
| 0 | 1 | format_version | uint8 | 1 |
| 1 | 1 | fw_version | uint8 | 1 |
| 2 | 2 | fleet_id | uint16 | 1 |
| 4 | 2 | device_id | uint16 | 1 |
| 6 | 4 | sequence_id | uint32 | 1 |
| 10 | 1 | battery_level_pct | uint8 | 1 (percent) |
| 11 | 1 | battery_health_pct | uint8 | 1 (percent) |
| 12 | 2 | solar_output_w | uint16 | 0.1 W |
| 14 | 1 | compute_util_pct | uint8 | 1 (percent) |
| 15 | 2 | compute_temp_c | int16 | 0.1 C |
| 17 | 1 | charging_state | uint8 | 0 or 1 |
| 18 | 2 | signal_strength_dbm | int16 | 0.1 dBm |
| 20 | 1 | datapoint_count | uint8 | number of datapoints |

Datapoint block (repeats `datapoint_count` times, 32 bytes each)

| Offset (relative) | Size (bytes) | Field | Type | Scale/Unit |
| --- | --- | --- | --- | --- |
| 0 | 2 | sample_offset_ms | uint16 | 1 ms from received_at |
| 2 | 2 | temperature_c | int16 | 0.1 C |
| 4 | 2 | humidity_pct | uint16 | 0.1 percent |
| 6 | 2 | co2_ppm | uint16 | 1 ppm |
| 8 | 2 | ozone_ppb | uint16 | 1 ppb |
| 10 | 2 | nitrogen_dioxide_ppb | uint16 | 1 ppb |
| 12 | 2 | sulfur_dioxide_ppb | uint16 | 1 ppb |
| 14 | 2 | pressure_hpa | uint16 | 0.1 hPa |
| 16 | 2 | solar_radiation_w_m2 | uint16 | 1 W/m^2 |
| 18 | 2 | salinity_psu | uint16 | 0.01 PSU |
| 20 | 2 | ph | uint16 | 0.01 pH |
| 22 | 2 | dissolved_oxygen_mg_l | uint16 | 0.01 mg/L |
| 24 | 2 | turbidity_ntu | uint16 | 0.01 NTU |
| 26 | 2 | electrical_conductivity_us_cm | uint16 | 1 uS/cm |
| 28 | 2 | metals_ug_l | uint16 | 1 ug/L |
| 30 | 2 | plastic_particles_m3 | uint16 | 1 particles/m^3 |

CRC
- CRC (2 bytes) is appended after the last datapoint block.
- Total payload length: `21 + (datapoint_count * 32) + 2` bytes.

# Structured-record-contract
The backend emits a structured record per payload. The contract is consistent across JSON, CSV, XML, and Avro.

Rules
- `received_at` is UTC ISO-8601 with millisecond precision: `YYYY-MM-DDTHH:MM:SS.mmmZ`.
- `payload` is base64 for text formats (JSON/CSV/XML) and raw bytes for Avro.

Canonical fields
- `received_at` (string)
- `payload` (string or bytes by format)
- `format_version` (int)
- `fw_version` (int)
- `fleet_id` (int)
- `device_id` (int)
- `sequence_id` (int)

Example: JSON (NDJSON line)
```json
{"received_at":"2026-02-12T14:05:12.347Z","payload":"AQEAAQABAAAACwRjZgE4A0gAAQAKAGQANwA7AA0AFAAXASkBBgEYAQIB6AC8AACrAAMAtwABvQABZgFjAQI=","format_version":1,"fw_version":1,"fleet_id":1,"device_id":1,"sequence_id":11}
```

Example: CSV
```csv
received_at,payload,format_version,fw_version,fleet_id,device_id,sequence_id
2026-02-12T14:05:12.347Z,AQEAAQABAAAACwRjZgE4A0gAAQAKAGQANwA7AA0AFAAXASkBBgEYAQIB6AC8AACrAAMAtwABvQABZgFjAQI=,1,1,1,1,11
```

Example: XML
```xml
<record>
  <received_at>2026-02-12T14:05:12.347Z</received_at>
  <payload>AQEAAQABAAAACwRjZgE4A0gAAQAKAGQANwA7AA0AFAAXASkBBgEYAQIB6AC8AACrAAMAtwABvQABZgFjAQI=</payload>
  <format_version>1</format_version>
  <fw_version>1</fw_version>
  <fleet_id>1</fleet_id>
  <device_id>1</device_id>
  <sequence_id>11</sequence_id>
</record>
```

Example: Avro (schema)
```json
{
  "type": "record",
  "name": "device_payload",
  "fields": [
    {"name": "received_at", "type": "string"},
    {"name": "payload", "type": "bytes"},
    {"name": "format_version", "type": "int"},
    {"name": "fw_version", "type": "int"},
    {"name": "fleet_id", "type": "int"},
    {"name": "device_id", "type": "int"},
    {"name": "sequence_id", "type": "long"}
  ]
}
```

# YAML-config-schema-and-CLI-overrides
The CLI can load a YAML config file and apply CLI overrides.

Required vs optional
- Required: none (all keys have defaults).
- Optional: all keys listed below.

Schema (defaults and validation)

| Key | Type | Default | Valid values / rules |
| --- | --- | --- | --- |
| output_format | string | json | one of `json`, `csv`, `xml`, `avro` |
| output_path | string | outputs/ | must be a writable directory path |
| number_of_dp | int | 1 | >= 1 |
| number_of_devices_per_fleet | int | 100 | >= 1 |
| number_of_fleets | int | 1 | >= 1 |
| dimensions | string or list | all | `all` or list of allowed dimension ids |
| rate_of_emitting_dp | string | 1 per minute | format: `<int> per <second|minute|hour>` |
| seed | int | 42 | >= 0 |
| start_time | string | now (UTC) | ISO-8601 UTC `YYYY-MM-DDTHH:MM:SS.mmmZ` |
| duration | string | 1 hour | format: `<int> <second|minute|hour|day>` |

Allowed dimension ids
- temperature
- humidity
- co2
- ozone
- nitrogen_dioxide
- sulfur_dioxide
- pressure
- solar_radiation
- salinity
- ph
- dissolved_oxygen
- turbidity
- electrical_conductivity
- metals
- plastic_particles

CLI flags (override YAML)
- `--config <path>` (YAML config file)
- `--output-format <json|csv|xml|avro>`
- `--output-path <path>`
- `--number-of-dp <int>`
- `--number-of-devices-per-fleet <int>`
- `--number-of-fleets <int>`
- `--dimensions <all|csv-list>` (e.g., `temperature,humidity,co2`)
- `--rate-of-emitting-dp "<int> per <second|minute|hour>"`
- `--seed <int>`
- `--start-time <ISO-8601 UTC>`
- `--duration "<int> <second|minute|hour|day>"`

Override precedence
- CLI flags override YAML values.
- YAML values override defaults.

Validation errors (examples)
- `output_format must be one of json,csv,xml,avro`
- `output_path is not writable: <path>`
- `number_of_dp must be >= 1`
- `number_of_devices_per_fleet must be >= 1`
- `number_of_fleets must be >= 1`
- `dimensions contains unknown values: <list>`
- `rate_of_emitting_dp must match '<int> per <second|minute|hour>'`
- `seed must be >= 0`
- `start_time must be UTC ISO-8601 with milliseconds`
- `duration must match '<int> <second|minute|hour|day>'`

# Validation-utilities
Optional checks can be enabled at generation time.

CLI flag
- `--validate` checks CRC-16 for every payload and verifies base64 round-trip for text formats.

Utility functions
- `src/validation.py` provides `verify_crc16(payload: bytes)` and `verify_base64_roundtrip(payload_b64: str)`.
