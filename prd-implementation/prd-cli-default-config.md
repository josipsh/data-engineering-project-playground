# Implementation Plan: CLI with Default Config Loading

## Source PRD
`prd/prd-cli-default-config.md`

---

## File Structure

```
src/
  main.py           — entry point: wires CLI → loader → Config, dispatches modes
  cli.py            — argparse setup, CLI-only concerns (args, help text)
  config.py         — Config domain model: enums, value objects, validation, factory
  config_loader.py  — IO only: reads YAML file, returns Config
config/
  sample.yaml       — sample config with valid dummy values for all parameters
tests/
  test_config.py    — unit tests for Config.from_dict (valid inputs, each validation error)
  test_config_loader.py — tests for load_config (file not found, unreadable, valid file)
  test_cli.py       — tests for parse_args (required --config, --validate-config flag)
```

---

## Dependencies

| Package | Purpose | How to add |
|---|---|---|
| `pyyaml` | Parse YAML config files | `uv add pyyaml` |
| `pytest` | Test runner | `uv add --dev pytest` |

`argparse` is stdlib.

---

## Domain Model (`src/config.py`)

All enums, validation logic, and the `Config` aggregate live here. Follows DDD: `Config` is always valid if it exists — the `from_dict` factory is the single entry point and enforces all invariants.

### Enums

```python
class OutputFormat(Enum):
    JSON                  = "json"
    JSON_WITH_BINARY_PAYLOAD = "json-with-binary-payload"
    XML                   = "xml"
    XML_WITH_BINARY_PAYLOAD  = "xml-with-binary-payload"
    CSV                   = "csv"
    CSV_WITH_BINARY_PAYLOAD  = "csv-with-binary-payload"
    AVRO                  = "avro"
    AVRO_WITH_BINARY_PAYLOAD = "avro_with_binary_payload"   # underscore — matches PRD exactly

class OutputType(Enum):
    KAFKA_ONLY     = "kafka-only"
    RABBITMQ_ONLY  = "rabbitmq-only"
    S3_ONLY        = "s3-only"
    S3_WITH_KAFKA  = "s3-with-kafka"
    S3_WITH_RABBITMQ = "s3-with-rabbitmq"

class SensorsDimensions(Enum):
    TEMPERATURE            = "temperature"
    HUMIDITY               = "humidity"
    CO2                    = "co2"
    OZONE                  = "ozone"
    NITROGEN_DIOXIDE       = "nitrogen_dioxide"
    BAROMETRIC_PRESSURE    = "barometric_pressure"
    SOLAR_RADIATION        = "solar_radiation"
    SALINITY               = "salinity"
    PH                     = "ph"
    PLASTICS               = "plastics"

class ComputerDimensions(Enum):
    CPU_TEMPERATURE  = "cpu_temperature"
    CPU_UTILIZATION  = "cpu_utilization"

class BatteryDimensions(Enum):
    BATTERY_TEMPERATURE      = "battery_temperature"
    BATTERY_PERCENTAGE_LEVEL = "battery_percentage_level"

class SolarPanelDimensions(Enum):
    CURRENT_VOLTAGE = "current_voltage"
    CURRENT_AMP     = "current_amp"

# Antenna has no dimensions — only a component-level error rate applies.

class EmitRate(Enum):
    ONE_PER_SECOND  = "1-per-second"
    TEN_PER_SECOND  = "10-per-second"
    ONE_PER_MINUTE  = "1-per-minute"
    TEN_PER_MINUTE  = "10-per-minute"
    ONE_PER_HOUR    = "1-per-hour"
    TEN_PER_HOUR    = "10-per-hour"

class ErrorRate(Enum):
    NONE     = 0.0
    LOW      = 0.1
    MEDIUM   = 0.25
    HIGH     = 0.5
    CRITICAL = 0.75
    CERTAIN  = 1.0
```

### Config Aggregate

```python
@dataclass(frozen=True)
class Config:
    output_format:               OutputFormat
    output_type:                 OutputType
    number_of_devices_per_fleet: int
    number_of_fleets:            int
    dimensions:                  frozenset[SensorsDimensions | ComputerDimensions |
                                           BatteryDimensions | SolarPanelDimensions] | Literal["all"]
    rate_of_emitting_dp:         EmitRate
    error_rate:                  dict[str, dict[str, ErrorRate] | ErrorRate] | None
```

- `frozen=True` prevents attribute reassignment after construction.
- `dimensions` is either the literal string `"all"` or a `frozenset` of typed dimension enum values.
- `error_rate` is `None` when omitted or set to `none` in the YAML. When present, maps component name (str) to either a single `ErrorRate` (for `antenna`) or a `dict[str, ErrorRate]` (dimension name → rate for all other components).

### Factory & Validation (`Config.from_dict`)

- Single classmethod entry point: `Config.from_dict(data: dict) -> Config`
- Collects **all** validation errors before raising, so the user sees every problem at once.
- Raises `ValueError` with one error per line.
- Private module-level helpers handle each field type:
  - `_parse_enum` — required enum fields (`output-format`, `output-type`, `rate-of-emitting-dp`)
  - `_parse_positive_int` — `number-of-devices-per-fleet`, `number-of-fleets`
  - `_parse_dimensions` — handles `"all"` vs. list, maps strings to typed enum values
  - `_parse_error_rate` — handles `None`/`"none"`, validates components and per-dimension rates
  - `_parse_error_rate_value` — maps a raw float to an `ErrorRate` enum member

**PyYAML note:** `error-rate: none` is parsed by PyYAML as Python `None`, same as omitting the key entirely. Both are treated identically.

### `__str__` Output

Flat `key: value` per line using original YAML key names (hyphenated):

```
output-format: json
output-type: kafka-only
number-of-devices-per-fleet: 50
number-of-fleets: 5
dimensions: all
rate-of-emitting-dp: 10-per-second
error-rate: sensors.temperature=low, sensors.humidity=medium, antenna=high
```

When `dimensions` is a frozenset, values are printed sorted and comma-separated.
When `error_rate` is `None`, prints `error-rate: none`.

---

## IO Layer (`src/config_loader.py`)

Pure IO — no validation logic:

```python
def load_config(path: str) -> Config:
    # open file → yaml.safe_load → Config.from_dict
```

Raises `FileNotFoundError` or `OSError` on file access failure.
Raises `ValueError` (from `Config.from_dict`) on invalid config content.

---

## CLI Layer (`src/cli.py`)

```python
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
```

Defines:
- `--config PATH` (required)
- `--validate-config` (flag, optional)

---

## Orchestration (`src/main.py`)

1. `parse_args()` → args
2. `load_config(args.config)` → config (exits with non-zero on any error, printing to stderr)
3. If `--validate-config`: print config, exit 0
4. Else: print `Executing started....`, exit 0

---

## Sample Config (`config/sample.yaml`)

```yaml
output-format: json
output-type: kafka-only
number-of-devices-per-fleet: 50
number-of-fleets: 5
dimensions: all
rate-of-emitting-dp: 10-per-second
error-rate:
  sensors:
    temperature: 0.1
    humidity: 0.25
  computer:
    cpu_temperature: 0.1
  antenna: 0.5
```

---

## Validation Rules Summary

| Parameter | Rule |
|---|---|
| `output-format` | Must be one of the 8 `OutputFormat` enum values |
| `output-type` | Must be one of the 5 `OutputType` enum values |
| `number-of-devices-per-fleet` | Must be a positive integer |
| `number-of-fleets` | Must be a positive integer |
| `dimensions` | `"all"` or a non-empty list of known dimension strings |
| `rate-of-emitting-dp` | Must be one of the 6 `EmitRate` enum values |
| `error-rate` | Optional. If present: valid component names, valid dimension names per component, float values matching an `ErrorRate` enum member |

All parameters except `error-rate` are required. Missing required parameters are reported explicitly by name.

---

## Testability Notes

Tests live in `tests/` at the project root.

- `Config.from_dict(dict)` can be called directly in tests without touching the filesystem.
- `config_loader.load_config(path)` can be tested by pointing at a temp file.
- `cli.parse_args(argv)` accepts a list, so no `sys.argv` patching needed.
- No monkey-patching required anywhere.
