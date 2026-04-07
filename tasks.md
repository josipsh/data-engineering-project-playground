# Task Breakdown (Dependency Ordered)

1) Repo layout (minimal)
- Create directories `src/`, `configs/`, `outputs/` [none]
- Add placeholder README section for structure (doc only) [none]
- Define initial module/file naming conventions [none]

2) Binary payload spec (happy path, scaled integers)
- Enumerate all payload fields needed for a record [1]
- Decide field order and byte sizes [2.1]
- Decide per-field scaling factors (e.g., temp * 10) [2.1]
- Define endianness for each field (big-endian) [2.2]
- Define CRC-16-CCITT-FALSE parameters and append position [2.2]
- Draft a payload layout table (offsets/size/type/scale) [2.2, 2.3, 2.4, 2.5]

3) Structured record contract
- Define `received_at` format and timezone rules [2]
- Define `payload` encoding by format (base64 vs bytes) [2]
- Draft canonical JSON/CSV/XML/Avro record fields [3.1, 3.2]
- Add examples of one record in each format [3.3]

4) YAML config schema + CLI overrides
- List required vs optional keys [1]
- Define default values for each key [4.1]
- Define valid value ranges/enums [4.1]
- Define CLI flags and mapping to schema keys [4.1]
- Define override precedence (CLI > YAML > default) [4.2, 4.4]
- Define validation errors/messages [4.2, 4.3, 4.5]

5) Generator core
- Define deterministic ID algorithm for fleets/devices [4]
- Define time generation algorithm from `start_time`, rate, duration [4]
- Define value ranges per dimension [2, 4]
- Define scaling step to integer values [2, 5.3]
- Define record assembly order before encoding [3, 5.1–5.4]

6) Payload encoder
- Implement field-to-bytes encoding helpers [2, 5]
- Implement big-endian packing per field [6.1]
- Implement CRC-16 function (per spec) [2.5]
- Append CRC to payload buffer [6.2, 6.3]
- Implement base64 for text outputs [3.2, 6.4]

7) Local writers
- Define output filename scheme and path rules [4]
- NDJSON writer (one line per record) [3, 5, 6]
- CSV writer (header + rows) [3, 5, 6]
- XML writer (one record per element) [3, 5, 6]
- Avro writer (schema + bytes payload) [3, 5, 6]

8) Validation utilities
- CRC verification for binary payload [6]
- Base64 round-trip checks for text formats [6]
- Optional validation CLI command or flag [4, 8.1, 8.2]

9) Documentation
- Add sample YAML config file [4]
- Document CLI usage and overrides [4]
- Document binary layout and scaling rules [2, 6]
- Provide end-to-end example output files [7]
