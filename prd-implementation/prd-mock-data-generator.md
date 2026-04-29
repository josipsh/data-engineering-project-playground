# Implementation: Mock Data Generator — Battery & Temperature Dimensions

## Source PRD
`prd/prd-mock-data-generator.md`

---

## File Structure

```
main.py                              — wires --stdout flag: calls DataGenerator, prints via _print_to_stdout
src/
  configs/
    cli.py                           — added is_stdout_enabled field and --stdout argparse flag
  generator/
    __init__.py
    models.py                        — DailyBounds, DeviceState, SimRecord, DeviceOutput dataclasses
    sine_generator.py                — SineGenerator: pure sine wave math
    device_simulator.py              — DeviceSimulator: generates 24 SimRecords for one device
    fleet_simulator.py               — FleetSimulator: randomises phase/bounds, creates DeviceSimulators
    data_generator.py                — DataGenerator: top-level orchestrator, takes Config
```

---

## Domain Model (`src/generator/`)

### Models (`models.py`)

```python
@dataclass
class DailyBounds:
    min_val: float
    max_val: float

@dataclass
class DeviceState:
    device_id: str
    battery_phase: float       # fleet offset + device offset, in radians
    temperature_phase: float
    battery_bounds: DailyBounds
    temperature_bounds: DailyBounds

@dataclass
class SimRecord:
    record_number: int         # per-device, starts at 1
    battery: float             # rounded to 2 decimal places
    temperature: float         # rounded to 2 decimal places

@dataclass
class DeviceOutput:
    device_id: str
    records: list[SimRecord]
```

### SineGenerator (`sine_generator.py`)

Stateless. Single method:

```python
def compute(self, step: int, total_steps: int, bounds: DailyBounds, phase_offset: float) -> float:
    angle = (2π * step / total_steps) + phase_offset
    normalized = (sin(angle) + 1) / 2          # maps [-1, 1] → [0, 1]
    value = bounds.min_val + normalized * (bounds.max_val - bounds.min_val)
    return round(value, 2)
```

One full cycle spans exactly `total_steps` steps. The trough maps to `min_val`, the peak to `max_val`.

### DeviceSimulator (`device_simulator.py`)

Takes a `DeviceState`, a shared `SineGenerator` instance, and `total_steps`. Iterates steps `0..total_steps-1`, calling `SineGenerator.compute` separately for battery and temperature using the device's own phase offsets and bounds. Returns a `DeviceOutput` with `record_number` starting at 1.

```python
class DeviceSimulator:
    def __init__(self, state: DeviceState, sine_generator: SineGenerator, total_steps: int) -> None
    def generate(self) -> DeviceOutput
```

### FleetSimulator (`fleet_simulator.py`)

Responsible for:
1. Sampling fleet-level random phase offsets once (one per dimension, independent).
2. For each device: sampling a device-level random phase offset (on top of fleet offset) and random daily bounds per dimension.
3. Creating and running a `DeviceSimulator` per device.

```python
class FleetSimulator:
    def __init__(self, fleet_id: int, device_count: int, sine_generator: SineGenerator, total_steps: int) -> None
    def generate(self) -> list[DeviceOutput]
```

**Phase offset ranges (radians):**

| Level | Range |
|---|---|
| Fleet | `U(-0.3, 0.3)` per dimension, sampled once per fleet |
| Device | `U(-0.15, 0.15)` per dimension, added on top of fleet offset |

**Daily bounds ranges:**

| Dimension | `min_val` | `max_val` |
|---|---|---|
| Battery (%) | `U(0.0, 50.0)` | `U(min + 10.0, 100.0)` |
| Temperature (°C) | `U(-10.0, 20.0)` | `U(min + 5.0, 45.0)` |

Min and max are rounded to 2 decimal places. The spread guarantees `max > min` by at least 10 (battery) or 5 (temperature).

**Device ID format:** `fleet-{fleet_id}-device-{device_index}` (1-indexed).

### DataGenerator (`data_generator.py`)

Top-level orchestrator. Takes a `Config`, resolves `total_steps` from `rate_of_emitting_dp`, creates one `FleetSimulator` per fleet, and collects all `DeviceOutput` results into a flat list.

```python
class DataGenerator:
    def __init__(self, config: Config) -> None
    def generate(self) -> list[DeviceOutput]
```

**Steps per simulated day:**

| `EmitRate` | Steps |
|---|---|
| `1-per-second` | 86 400 |
| `10-per-second` | 864 000 |
| `1-per-minute` | 1 440 |
| `10-per-minute` | 14 400 |
| `1-per-hour` | 24 |
| `10-per-hour` | 240 |

For this iteration the config is expected to use `1-per-hour` (24 steps). The mapping is complete so other rates work without code changes.

---

## CLI Layer (`src/configs/cli.py`)

`CliParsedArgs` gained one field:

```python
@dataclass
class CliParsedArgs:
    config_filepath: str
    is_validate_config_enabled: bool
    is_stdout_enabled: bool          # new
```

`parse_args` gained one flag:

```
--stdout    Print generated records to the terminal instead of any configured output
```

---

## Orchestration (`main.py`)

New execution path inserted before the existing stub:

```python
if cli_args.is_stdout_enabled:
    outputs = DataGenerator(parsed_config).generate()
    _print_to_stdout(outputs)
    return
```

`_print_to_stdout` is a module-level function in `main.py` (dev-only, not in `src/`):

```python
def _print_to_stdout(outputs: list[DeviceOutput]) -> None:
    for device_output in outputs:
        print(device_output.device_id)
        for record in device_output.records:
            print(f"{record.record_number} - {record.battery} | {record.temperature}")
        print("-----------")
```

When `--stdout` is active all output configuration (format, type, backend) is ignored. No warning or error is produced.

---

## Stdout Output Format

```
<device_id>
<record_number> - <battery> | <temperature>
...
-----------
```

- `device_id`: `fleet-{n}-device-{m}`, 1-indexed
- `record_number`: per-device sequential integer starting at 1
- `battery` / `temperature`: decimal with 2 decimal places (Python default `str(float)` — no zero-padding)
- Separator `-----------` follows the last record of every device block, including the last device

---

## Constraints

- Battery values are always within their randomly assigned daily bounds.
- Temperature values are always within their randomly assigned daily bounds.
- Battery theoretical bounds: 0–100 (%).
- Temperature theoretical bounds: -10–45 (°C).
- Phase offsets and daily bounds are re-randomised each run — no seed is set.
- Output is sequential: devices are processed one at a time, no concurrency.
- Exactly 1 simulated day is generated per run.

---

## Testability Notes

- `SineGenerator.compute` is a pure function with no state — unit-testable directly.
- `DeviceSimulator` accepts injected `SineGenerator` and `DeviceState` — no monkey-patching needed.
- `FleetSimulator` uses `random.uniform` directly; tests that verify exact values must seed `random` beforehand.
- `DataGenerator` accepts a `Config` instance — no filesystem access required in tests.
- `_print_to_stdout` in `main.py` accepts a `list[DeviceOutput]` — testable by passing pre-built fixtures and capturing stdout.
