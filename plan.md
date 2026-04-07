# Implementation Plan

1. Repo layout (minimal)
   - `src/` for code, `configs/` for YAML examples, `outputs/` for generated files.
2. Binary payload spec (happy path, scaled integers)
   - Field order, sizes, endianness (big-endian).
   - Use integer scaling per dimension (e.g., temp in tenths of °C) and document each scale.
   - Append CRC-16-CCITT-FALSE (poly `0x1021`, init `0xFFFF`, xorout `0x0000`, no reflect), 2 bytes big-endian.
3. Structured record contract
   - `received_at`: UTC ISO-8601 with millisecond precision (`YYYY-MM-DDTHH:MM:SS.mmmZ`), string.
   - `payload`: base64 in JSON/CSV/XML; raw bytes in Avro.
4. YAML config schema + CLI overrides
   - Keys: `output_format`, `output_path`, `number_of_dp`, `number_of_devices_per_fleet`, `number_of_fleets`, `dimensions`, `rate_of_emitting_dp`, `seed`, `start_time`, `duration`.
   - CLI flags override YAML; validate allowed values and defaults.
5. Generator core
   - Deterministic fleet/device IDs derived from seed.
   - Timestamp generation from `start_time` + rate + duration.
   - Value generation per dimension within sensible ranges, scaled to integers.
6. Payload encoder
   - Build byte buffer per record.
   - Compute CRC-16 and append.
   - Base64 encode for text formats.
7. Local writers
   - NDJSON: one record per line.
   - CSV: header + rows.
   - XML: one record per element with `received_at` and `payload`.
   - Avro: schema with `received_at` (string) and `payload` (bytes).
8. Validation utilities
   - Verify CRC-16 on generated payload.
   - Base64 round-trip check for text formats.
9. Documentation
   - Add sample YAML config and CLI usage to `README.md`.
   - Document binary layout and scaling rules.
