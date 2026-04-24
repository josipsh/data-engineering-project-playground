# Implementation Plan: CLI with Default Config Loading

## Source PRD
`prd/prd-cli-default-config.md`

---

## File Structure

```
main.py                              — entry point: wires CLI → loader → Config, dispatches modes
src/
  configs/
    cli.py                           — argparse setup, returns CliParsedArgs dataclass
    config.py                        — Config aggregate + component dimension dataclasses + validation
    config_parameters_enums.py       — ConfigParameters and Components enums
    dimensions_enums.py              — SensorDimension, ComputerDimension, BatteryDimension, SolarPanelDimension
    output_enums.py                  — OutputFormat, OutputType
    rate_enums.py                    — EmitRate, ErrorRate
  errors/
    config_error.py                  — ConfigError (raised on invalid config content)
    yaml_error.py                    — YamlError (raised on file access failure)
  utils/
    yaml_loader.py                   — IO only: reads YAML file, returns raw dict
config/
  sample.yaml                        — sample config with valid dummy values for all parameters
tests/
  configs/
    test_cli.py                      — tests for parse_args
    test_config_positive_cases.py    — Config.from_dict with valid inputs
    test_config_negative_cases.py    — Config.from_dict with each validation error
    value_consts.py                  — shared test constants
  utils/
    test_yaml_loader.py              — tests for yaml_loader.load (file not found, unreadable, valid)
```

---

## Dependencies

| Package | Purpose | How to add |
|---|---|---|
| `pyyaml` | Parse YAML config files | `uv add pyyaml` |
| `pytest` | Test runner | `uv add --dev pytest` |

`argparse` is stdlib.

---

## Domain Model (`src/configs/`)

Enums and validation logic are split across several files. The `Config` aggregate and all dimension dataclasses live in `config.py`. Follows DDD: `Config` is always valid if it exists — the `from_dict` factory is the single entry point and enforces all invariants.

### Enums (`src/configs/output_enums.py`, `rate_enums.py`, `dimensions_enums.py`, `config_parameters_enums.py`)

```python
# output_enums.py
class OutputFormat(Enum):
    JSON                     = "json"
    XML                      = "xml"
    CSV                      = "csv"
    AVRO                     = "avro"
    JSON_WITH_BINARY_PAYLOAD = "json-with-binary-payload"
    XML_WITH_BINARY_PAYLOAD  = "xml-with-binary-payload"
    CSV_WITH_BINARY_PAYLOAD  = "csv-with-binary-payload"
    AVRO_WITH_BINARY_PAYLOAD = "avro-with-binary-payload"

class OutputType(Enum):
    KAFKA_ONLY       = "kafka-only"
    RABBITMQ_ONLY    = "rabbitmq-only"
    S3_ONLY          = "s3-only"
    S3_WITH_KAFKA    = "s3-with-kafka"
    S3_WITH_RABBITMQ = "s3-with-rabbitmq"

# rate_enums.py
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

# dimensions_enums.py  — all values use hyphens as separators
class SensorDimension(Enum):
    TEMPERATURE         = "temperature"
    HUMIDITY            = "humidity"
    CO2                 = "co2"
    OZONE               = "ozone"
    NITROGEN_DIOXIDE    = "nitrogen-dioxide"
    BAROMETRIC_PRESSURE = "barometric-pressure"
    SOLAR_RADIATION     = "solar-radiation"
    SALINITY            = "salinity"
    PH                  = "ph"
    PLASTICS            = "plastics"

class ComputerDimension(Enum):
    CPU_TEMPERATURE = "cpu-temperature"
    CPU_UTILIZATION = "cpu-utilization"

class BatteryDimension(Enum):
    BATTERY_TEMPERATURE      = "battery-temperature"
    BATTERY_PERCENTAGE_LEVEL = "battery-percentage-level"

class SolarPanelDimension(Enum):
    CURRENT_VOLTAGE = "current-voltage"
    CURRENT_AMP     = "current-amp"

# config_parameters_enums.py
class ConfigParameters(Enum):
    OUTPUT_FORMAT               = "output-format"
    OUTPUT_TYPE                 = "output-type"
    NUMBER_OF_DEVICES_PER_FLEET = "number-of-devices-per-fleet"
    NUMBER_OF_FLEETS            = "number-of-fleets"
    RATE_OF_EMITTING_DP         = "rate-of-emitting-dp"
    ERROR_RATE                  = "error-rate"
    DIMENSIONS                  = "dimensions"

class Components(Enum):
    SENSORS     = "sensors"
    COMPUTER    = "computer"
    BATTERY     = "battery"
    SOLAR_PANEL = "solar-panel"
```

### Dimension value dataclasses (`src/configs/config.py`)

Each measurable dimension is represented as a `DimensionValue` carrying its enabled state and error rate. Component-level dataclasses group the values and provide `from_dict` factories.

```python
@dataclass()
class DimensionValue:
    is_enabled: bool
    error_rate: ErrorRate

    def to_dict(self) -> dict: ...

@dataclass()
class SensorDimensions:
    temperature: DimensionValue
    humidity: DimensionValue
    co2: DimensionValue
    ozone: DimensionValue
    nitrogen_dioxide: DimensionValue
    barometric_pressure: DimensionValue
    solar_radiation: DimensionValue
    salinity: DimensionValue
    ph: DimensionValue
    plastics: DimensionValue

    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(
        dimension_data: list[SensorDimension],
        error_rate: dict[SensorDimension, ErrorRate]
    ) -> "SensorDimensions": ...

# ComputerDimensions, BatteryDimensions, SolarPanelDimensions follow the same pattern.

@dataclass()
class Dimensions:
    sensors:     SensorDimensions
    computer:    ComputerDimensions
    battery:     BatteryDimensions
    solar_panel: SolarPanelDimensions

    def to_dict(self) -> dict: ...
```

### Config Aggregate (`src/configs/config.py`)

```python
@dataclass()
class Config:
    output_format:               OutputFormat
    output_type:                 OutputType
    number_of_devices_per_fleet: int
    number_of_fleets:            int
    dimensions:                  Dimensions
    rate_of_emitting_dp:         EmitRate
```

- `error_rate` is **not** a top-level field — it is embedded inside each `DimensionValue.error_rate` within `dimensions`.
- The dataclass is **not** frozen.

### Factory & Validation (`Config.from_dict`)

- Single classmethod entry point: `Config.from_dict(data: dict) -> Config`
- Collects **all** validation errors before raising, so the user sees every problem at once.
- Raises `ConfigError` with one error per line.
- Also raises `ConfigError` if unrecognised parameter keys are present (guards against typos).
- Private module-level helpers handle each field type:
  - `_parse_enum` — required enum fields (`output-format`, `output-type`, `rate-of-emitting-dp`)
  - `_parse_positive_int` — `number-of-devices-per-fleet`, `number-of-fleets`
  - `_parse_dimensions` — handles `"all"` vs. list; resolves error rates per component
  - `_get_valid_error_rates` — validates component names and delegates per-dimension validation
  - `_get_valid_error_rate_data` — validates dimension name and maps raw float to `ErrorRate` enum
  - `_check_if_unsupported_parameter_is_provided` — rejects unknown top-level keys

**Error rate values:** only the six exact `ErrorRate` enum values are accepted (`0.0`, `0.1`, `0.25`, `0.5`, `0.75`, `1.0`). Any other float is invalid.

**Omitted `error-rate` key:** `data.get('error-rate', {})` returns `{}`, so all dimension error rates default to `ErrorRate.NONE`. The key must be **omitted** to get this behaviour — providing `error-rate: none` (which PyYAML parses as Python `None`) is treated as an invalid value.

### `to_dict()` Output

Returns a nested dict using original YAML key names (hyphenated). Printed in `main.py` via `yaml.dump(config.to_dict())`:

```yaml
dimensions:
  battery:
    battery-percentage-level:
      error_rate: NONE
      is_enabled: true
    battery-temperature:
      error_rate: NONE
      is_enabled: true
  ...
number-of-devices-per-fleet: 50
number-of-fleets: 5
output-format: json
output-type: kafka-only
rate-of-emitting-dp: 10-per-second
```

---

## IO Layer (`src/utils/yaml_loader.py`)

Pure IO — no validation logic:

```python
def load(path: str) -> dict[str, Any]:
    # open file → yaml.safe_load → return raw dict
```

Raises `YamlError` on file-not-found or any other read failure. `Config` construction is done separately in `main.py` via `Config.from_dict(loaded_dict)`.

---

## CLI Layer (`src/configs/cli.py`)

```python
@dataclass
class CliParsedArgs:
    config_filepath: str
    is_validate_config_enabled: bool

def parse_args(argv: list[str]) -> CliParsedArgs:
```

Defines:
- `--config PATH` (required)
- `--validate-config` (flag, optional)

Returns a typed `CliParsedArgs` dataclass, not a raw `argparse.Namespace`.

---

## Orchestration (`main.py`)

1. `cli.parse_args(sys.argv[1:])` → `CliParsedArgs`
2. `yaml_loader.load(args.config_filepath)` → raw dict (raises `YamlError` on failure)
3. `Config.from_dict(loaded_dict)` → `Config` (raises `ConfigError` on invalid content)
4. Any exception is caught, printed to stderr, and exits with code `1`
5. If `--validate-config`: `yaml.dump(config.to_dict())` → stdout, exit 0
6. Else: print `Executing started....`, exit 0

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
    cpu-temperature: 0.1
```

---

## Validation Rules Summary

| Parameter | Rule |
|---|---|
| `output-format` | Must be one of the 8 `OutputFormat` enum values |
| `output-type` | Must be one of the 5 `OutputType` enum values |
| `number-of-devices-per-fleet` | Must be a positive integer |
| `number-of-fleets` | Must be a positive integer |
| `dimensions` | `"all"` or a non-empty list of known hyphenated dimension strings |
| `rate-of-emitting-dp` | Must be one of the 6 `EmitRate` enum values |
| `error-rate` | Optional. If present: valid component names (`sensors`, `computer`, `battery`, `solar-panel`), valid hyphenated dimension names per component, float values matching an `ErrorRate` enum member exactly |
| _(any unknown key)_ | Rejected as unsupported parameter |

All parameters except `error-rate` are required. Missing required parameters are reported explicitly by name. All errors are collected and reported together.

---

## Testability Notes

Tests live in `tests/` at the project root, mirroring the `src/` structure.

- `Config.from_dict(dict)` can be called directly in tests without touching the filesystem.
- `yaml_loader.load(path)` can be tested by pointing at a temp file or a fixture file.
- `cli.parse_args(argv)` accepts a list, so no `sys.argv` patching needed.
- No monkey-patching required anywhere.
- Config tests are split into `test_config_positive_cases.py` and `test_config_negative_cases.py`. Shared constants live in `value_consts.py`.
