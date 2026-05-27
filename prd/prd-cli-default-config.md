# PRD: CLI with Default Config Loading

## 1. Introduction / Overview

This feature introduces the entry point for the mock data generator: a command-line interface (CLI) that accepts a path to a YAML configuration file, loads and validates it, and either prints the configuration or begins the mocking flow.

At this stage, all configuration comes exclusively from the file — there are no CLI flag overrides. Two modes of operation are supported: a validate-and-print mode and an execute mode (stubbed for now).

**Problem it solves:** Without a config-loading layer, there is no way to pass structured parameters to any other part of the system. This step establishes the configuration contract that all future components will depend on.

---

## 2. Goals

- Allow the user to supply a YAML config file via a CLI argument.
- Parse and validate all required configuration parameters from that file.
- Represent the configuration as a single, reusable object that can be passed to any downstream component.
- Support a `--validate-config` flag that prints the validated configuration and exits.
- When `--validate-config` is not provided, validate the config and then start the mocking flow (stubbed as a printed message for now).
- Fail with a clear error message if the config file is missing, unreadable, or contains invalid values.

---

## 3. User Stories

- **As a developer**, I want to run the CLI with `--validate-config` so that I can verify my configuration is correct before running the full pipeline.
- **As a developer**, I want the CLI to reject invalid config values immediately — in both modes — so that the mocking flow never starts with a broken configuration.
- **As a developer**, I want the config represented as a single object so that I can pass it to any future component without reading the file again.

---

## 4. Functional Requirements

### 4.1 CLI Arguments

1. The CLI must accept a required argument `--config` with the path to a YAML configuration file (e.g., `--config config/sample.yaml`).
2. The CLI must accept an optional flag `--validate-config`. When present, the CLI runs in validate-and-print mode. When absent, it runs in execute mode.
3. If `--config` is not provided, the CLI must exit with a non-zero status code and print a usage error to stderr.
4. If the specified file does not exist or cannot be read, the CLI must exit with a non-zero status code and print a descriptive error message to stderr.

### 4.2 Configuration Parameters

The config file must define all of the following parameters. All parameters are required except `error-rate`, which is optional — if omitted, no errors are injected (all error rates default to `none`).

| Parameter | Expected Values |
|---|---|
| `output-format` | One of: `json`, `json-with-binary-payload`, `xml`, `xml-with-binary-payload`, `csv`, `csv-with-binary-payload`, `avro`, `avro-with-binary-payload` |
| `output-type` | One of: `kafka-only`, `rabbitmq-only`, `s3-only`, `s3-with-kafka`, `s3-with-rabbitmq` |
| `number-of-devices-per-fleet` | Positive integer |
| `number-of-fleets` | Positive integer |
| `dimensions` | Either the literal string `all`, or a list of one or more values from the full set of valid dimensions across all components (see 4.3) |
| `rate-of-emitting-dp` | One of: `1-per-second`, `10-per-second`, `1-per-minute`, `10-per-minute`, `1-per-hour`, `10-per-hour` |
| `error-rate` | **Optional.** If omitted, all error rates default to `none` (no errors injected). When provided, must use a nested YAML mapping structure keyed by component (see 4.4). |

### 4.3 Valid Dimension Values

Each device component exposes its own set of measurable dimensions. When `dimensions` is `all`, all dimensions from all components are included. Otherwise, each named value must belong to the set below. All dimension values use hyphens as separators.

**`sensors` component (10 dimensions):**
`temperature`, `humidity`, `co2`, `ozone`, `nitrogen-dioxide`, `barometric-pressure`, `solar-radiation`, `salinity`, `ph`, `plastics`

**`computer` component (2 dimensions):**
`cpu-temperature`, `cpu-utilization`

**`battery` component (2 dimensions):**
`battery-temperature`, `battery-percentage-level`

**`solar-panel` component (2 dimensions):**
`current-voltage`, `current-amp`

### 4.4 Error Rate Format

When `error-rate` is omitted from the config file, all error rates default to `none` — no errors are injected.

When `error-rate` is explicitly provided, it must use a nested YAML mapping structure keyed by component. Each component supports its own set of per-dimension rates, matching the dimension sets defined in 4.3.

| Component | Per-dimension keys available |
|---|---|
| `sensors` | `temperature`, `humidity`, `co2`, `ozone`, `nitrogen-dioxide`, `barometric-pressure`, `solar-radiation`, `salinity`, `ph`, `plastics` |
| `computer` | `cpu-temperature`, `cpu-utilization` |
| `battery` | `battery-temperature`, `battery-percentage-level` |
| `solar-panel` | `current-voltage`, `current-amp` |

Each rate must be one of the following exact values: `0.0`, `0.1`, `0.25`, `0.5`, `0.75`, `1.0`. Only the components and dimensions that should have errors need to be listed — any entry omitted from the map defaults to `0.0` (no errors).

### 4.5 Validation Behavior

5. If any required parameter (all except `error-rate`) is missing from the config file, the CLI must exit with a non-zero status code and print which parameter is missing to stderr.
6. If any parameter contains an invalid value, the CLI must exit with a non-zero status code and print which parameter is invalid and what values are expected, to stderr.
7. All validation errors are collected before reporting — the user sees every problem at once, not just the first one.
8. Validation must run in both `--validate-config` mode and execute mode — the mocking flow must never start with an invalid config.
9. If an unrecognised parameter key is present in the config file, the CLI must report it as an error (guards against typos).

### 4.6 Config Object

10. On successful validation, the configuration must be represented as a single config object that encapsulates all parameters.
11. The config object exposes a `to_dict()` method that returns a nested dictionary of all parameters, using the original YAML key names (hyphenated). The `dimensions` key maps to a nested structure organised by component, then by dimension, each with `is_enabled` and `error_rate` fields.

### 4.7 Validate-and-Print Mode (`--validate-config`)

12. After successful validation, the CLI must print the config object (via `yaml.dump(config.to_dict())`) to stdout and exit with status code `0`.

### 4.8 Execute Mode (no `--validate-config`)

13. After successful validation, the CLI must print `Executing started....` to stdout and exit with status code `0`.
14. No data generation or further processing is required at this stage.

### 4.9 Sample Config File

15. A sample config file must be included at `config/sample.yaml` with valid dummy values for all parameters. This file serves as a reference for users.

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

## 5. Non-Goals (Out of Scope)

- CLI flag overrides of config values — covered in a separate PRD.
- Any actual data generation or output beyond the stub message.
- Support for config formats other than YAML.
- Hot-reloading or watching the config file for changes.

---

## 6. Constraints & Dependencies

- The config file format is YAML.
- The `config/` directory must exist at the project root.
- The CLI entry point is `main.py` at the project root.

---

## 7. Success Metrics

- Running `uv run python main.py --config config/sample.yaml --validate-config` prints the config as nested YAML and exits with code `0`.
- Running `uv run python main.py --config config/sample.yaml` (without `--validate-config`) prints `Executing started....` and exits with code `0`.
- Running with a missing parameter, an invalid value, or a non-existent file prints an error to stderr and exits with a non-zero code — in both modes.
- No component other than the CLI entry point needs to re-read the config file — all downstream use goes through the config object.

---

## 8. Open Questions

None.
