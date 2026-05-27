# PRD: Mock Data Generator — Battery & Temperature Dimensions

## 1. Introduction / Overview

This document describes the first iteration of the mock data generation feature for the CLI tool. It covers two measurable dimensions — **battery utilization** and **temperature** — and a development-only `--stdout` flag that allows developers to inspect generated records directly in the terminal without configuring any output backend.

The generated data must feel realistic: values rise and fall once per simulated day following a sinusoidal curve, mimicking a sensor device that charges via a solar panel during daylight and discharges at night, and that experiences real-world temperature swings across the day.

---

## 2. Goals

- Generate per-device, per-data-point values for battery utilization and temperature that follow a sinusoidal pattern across a simulated day.
- Introduce controlled variety: each simulated day gets a freshly randomised min/max range for each dimension, so no two days look identical.
- Introduce slight per-device and per-fleet phase variation so devices within the same fleet do not produce identical output.
- Provide a `--stdout` flag so developers can verify generated data visually in the terminal during development, without any output backend.
- Make the simulation speed configurable based on the emit-rate configuration parameter

---

## 3. User Stories

**As a developer**, I want to run the CLI with `--stdout` so I can see generated records printed to the terminal without setting up any file, Kafka, or S3 output.

**As a developer**, I want battery and temperature values to follow a sine wave pattern so that the data visually resembles real sensor readings when I inspect it.

**As a developer**, I want each simulated day to have randomly assigned min/max boundaries per dimension so that repeated runs produce varied data.

**As a developer**, I want each device and fleet to have a slightly different phase offset so that the data set does not look artificially uniform.

**As a developer**, I want to control how fast one simulated day runs so I can verify a full cycle quickly during development without waiting.

---

## 4. Functional Requirements

### 4.1 Dimensions

1. The system must generate data for exactly two dimensions in this iteration: **battery utilization** and **temperature**.
2. Battery utilization must be expressed as a percentage. Its theoretical bounds are **0 to 100** (inclusive).
3. Temperature must be expressed in **degrees Celsius**. Its theoretical bounds are **-10 to 45** (inclusive).
4. Battery utilization and temperature must be generated as **independent** sine waves — each has its own randomly assigned daily min/max and its own phase.

### 4.2 Per-Day Random Min/Max

5. At the start of each simulated day, the system must randomly assign a **min** and a **max** value for each dimension independently, within that dimension's theoretical bounds.
   - Example battery: min = 30, max = 95
   - Example temperature: min = 8, max = 38
6. The randomly assigned min and max must remain constant for the entire simulated day.
7. The generated values for a dimension must never fall below the daily min or rise above the daily max.

### 4.3 Sinusoidal Value Pattern

8. The value of each dimension at each data point must follow a **sinusoidal curve** where:
   - The **peak** of the curve equals the daily max value for that dimension.
   - The **trough** of the curve equals the daily min value for that dimension.
9. One full sine wave cycle (360°) must span exactly **one simulated day**, starting from 00:00.
10. The number of data points per simulated day is derived from the `rate-of-emitting-dp` configuration:
    - `1-per-second` → 86,400 data points
    - `10-per-second` → 864,000 data points
    - `1-per-minute` → 1,440 data points
    - `10-per-minute` → 14,400 data points
    - `1-per-hour` → 24 data points
    - `10-per-hour` → 240 data points
11. The smoothness of the sine wave curve is a natural consequence of the emitting rate — a higher rate produces more samples and a smoother curve.
12. All generated values must be rounded to **2 decimal places**.

### 4.4 Phase Offset

13. Each **fleet** must have a slight random phase offset applied to the sine wave of all devices within it.
14. Each **device** must have an additional slight random phase offset applied on top of its fleet's offset.
15. The combined offset must be small enough that devices within the same fleet are clearly correlated, yet perceptibly different from one another.
16. The phase offset must apply to both dimensions independently; i.e., battery and temperature each receive their own offset per device/fleet.

### 4.5 Simulation Speed

17. For this iteration, `rate-of-emitting-dp` is hardcoded to `1-per-hour`, producing **24 data points** per simulated day.
18. The speed setting must apply equally to battery utilization and temperature.

### 4.6 Data Volume

20. The system must generate data for **exactly 1 simulated day** per run in this iteration. Combined with the `1-per-hour` rate, this means **24 total records per device**. The number of days will be made configurable in a future iteration.

### 4.7 `--stdout` Flag

21. The CLI must support a `--stdout` flag.
22. When `--stdout` is active, the system must print records for each device sequentially (synchronous — no concurrency in this iteration).
23. Before printing a device's records, the system must print the device identifier on its own line (e.g., `device-1`, `device-2`).
24. After printing all records for a device, the system must print a separator line (e.g., `-----------`) before the next device.
25. Each record must follow this format, one per line:

    ```
    <record_number> - <battery_utilization> | <temperature>
    ```

    Example output for two devices:
    ```
    device-1
    1 - 87.43 | 21.56
    2 - 87.51 | 21.62
    3 - 87.60 | 21.69
    -----------
    device-2
    1 - 86.12 | 20.34
    2 - 86.20 | 20.41
    3 - 86.29 | 20.48
    -----------
    ```

26. `record_number` is a **per-device** counter, starting at 1 for each device's first record.
27. When `--stdout` is active, the system must **ignore all output configuration** (file path, Kafka, RabbitMQ, S3, Avro format, etc.).
28. The `--stdout` flag must not be required for normal CLI operation.
29. There must be no warning, error, or log message discouraging the use of `--stdout` at runtime — it is simply not included in production usage documentation.

---

## 5. Non-Goals (Out of Scope)

- Generating data for any dimension other than battery utilization and temperature.
- Writing output to any file format (JSON, CSV, XML, Avro) or any streaming/storage backend.
- Defining start and end dates for generation (planned for a future iteration).
- Generating data for more than one simulated day.
- Temperature in Fahrenheit.
- Any form of data replay or time-travel simulation.
- Validation or enforcement against `--stdout` being used in production environments.

---

## 6. Design Considerations

### Console Output Format

Output is grouped per device. Each device block follows this structure:

```
<device_id>
<record_number> - <battery_utilization> | <temperature>
...
-----------
```

- `device_id`: the device label, e.g., `device-1`, `device-2`.
- `record_number`: a per-device sequential integer starting at 1.
- `battery_utilization`: a decimal number with exactly 2 decimal places (e.g., `87.43`).
- `temperature`: a decimal number with exactly 2 decimal places (e.g., `21.56`).
- Records within a device block are separated by a newline character.
- A separator line (e.g., `-----------`) follows the last record of each device block.

---

## 7. Constraints & Dependencies

- This feature depends on the existing `rate-of-emitting-dp` configuration being read and parsed correctly by the CLI.
- The `--stdout` flag must not conflict with any existing CLI flags.
- The `--stdout` flag is a **development-only** flag and is expected to be removed in a future iteration once file/stream output is implemented and verified.

---

## 8. Success Metrics

- Running the CLI with `--stdout` produces console output matching the specified format with no additional noise.
- Battery values for every record fall within the randomly assigned daily min/max for that run.
- Temperature values for every record fall within the randomly assigned daily min/max for that run.
- Plotting the output values for a single device over all records produces a clearly recognizable sine wave shape.
- Changing the simulation speed parameter changes how quickly one full cycle completes in real time.
- Different devices within the same fleet produce values that are similar but not identical, due to the phase offset.
- Different fleets produce values with a slightly different phase from one another.

---

## 9. Open Questions

None at this time.
