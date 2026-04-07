from __future__ import annotations

import argparse
import os
from pathlib import Path

import base64
import yaml

from src.generator_core import GeneratorConfig, generate_records
from src.validation import verify_base64_roundtrip, verify_crc16
from src.writers import write_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mock device payloads")
    parser.add_argument("--config", type=str, help="Path to YAML config")
    parser.add_argument("--output-format", type=str, help="json|csv|xml|avro")
    parser.add_argument("--output-path", type=str, help="Output directory path")
    parser.add_argument(
        "--number-of-dp", type=int, help="Number of datapoints per record"
    )
    parser.add_argument("--number-of-devices-per-fleet", type=int)
    parser.add_argument("--number-of-fleets", type=int)
    parser.add_argument("--dimensions", type=str, help="all or csv list")
    parser.add_argument("--rate-of-emitting-dp", type=str)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--start-time", type=str)
    parser.add_argument("--duration", type=str)
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate CRC and base64 round-trip",
    )
    args = parser.parse_args()

    config_data = _load_yaml(args.config)
    config_data = _apply_overrides(config_data, args)
    _validate_config(config_data)

    config = GeneratorConfig(
        output_format=config_data.get("output_format", "json"),
        output_path=config_data.get("output_path", "outputs/"),
        number_of_dp=config_data.get("number_of_dp", 1),
        number_of_devices_per_fleet=config_data.get("number_of_devices_per_fleet", 100),
        number_of_fleets=config_data.get("number_of_fleets", 1),
        dimensions=config_data.get("dimensions", "all"),
        rate_of_emitting_dp=config_data.get("rate_of_emitting_dp", "1 per minute"),
        seed=config_data.get("seed", 42),
        start_time=config_data.get("start_time"),
        duration=config_data.get("duration", "1 hour"),
    )

    records = generate_records(config)
    if args.validate:
        records = _validated_records(records, config.output_format)
    output_file = write_records(records, config.output_format, config.output_path)
    print(f"Wrote {config.output_format} output to {output_file}")


def _load_yaml(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def _apply_overrides(config_data: dict, args: argparse.Namespace) -> dict:
    overrides = {
        "output_format": args.output_format,
        "output_path": args.output_path,
        "number_of_dp": args.number_of_dp,
        "number_of_devices_per_fleet": args.number_of_devices_per_fleet,
        "number_of_fleets": args.number_of_fleets,
        "dimensions": args.dimensions,
        "rate_of_emitting_dp": args.rate_of_emitting_dp,
        "seed": args.seed,
        "start_time": args.start_time,
        "duration": args.duration,
    }
    for key, value in overrides.items():
        if value is not None:
            config_data[key] = value
    return config_data


def _validate_config(config_data: dict) -> None:
    output_format = config_data.get("output_format", "json")
    if output_format not in {"json", "csv", "xml", "avro"}:
        raise ValueError("output_format must be one of json,csv,xml,avro")

    output_path = config_data.get("output_path", "outputs/")
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not os.access(output_dir, os.W_OK):
        raise ValueError(f"output_path is not writable: {output_path}")

    for key in ("number_of_dp", "number_of_devices_per_fleet", "number_of_fleets"):
        value = config_data.get(key)
        if value is not None and int(value) < 1:
            raise ValueError(f"{key} must be >= 1")

    seed = config_data.get("seed")
    if seed is not None and int(seed) < 0:
        raise ValueError("seed must be >= 0")


def _validated_records(records, output_format: str):
    for record in records:
        if not verify_crc16(record.payload):
            raise ValueError("CRC validation failed for payload")
        if output_format in {"json", "csv", "xml"}:
            payload_b64 = base64.b64encode(record.payload).decode("ascii")
            if not verify_base64_roundtrip(payload_b64):
                raise ValueError("Base64 round-trip validation failed")
        yield record


if __name__ == "__main__":
    main()
