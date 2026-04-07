from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import Random
from typing import Iterable, Iterator

from src.payload_encoder import Datapoint, PayloadHeader, encode_payload


DIMENSION_IDS = [
    "temperature",
    "humidity",
    "co2",
    "ozone",
    "nitrogen_dioxide",
    "sulfur_dioxide",
    "pressure",
    "solar_radiation",
    "salinity",
    "ph",
    "dissolved_oxygen",
    "turbidity",
    "electrical_conductivity",
    "metals",
    "plastic_particles",
]


@dataclass(frozen=True)
class GeneratorConfig:
    output_format: str = "json"
    output_path: str = "outputs/"
    number_of_dp: int = 1
    number_of_devices_per_fleet: int = 100
    number_of_fleets: int = 1
    dimensions: str | list[str] = "all"
    rate_of_emitting_dp: str = "1 per minute"
    seed: int = 42
    start_time: str | None = None
    duration: str = "1 hour"


@dataclass(frozen=True)
class GeneratedRecord:
    received_at: str
    payload: bytes
    format_version: int
    fw_version: int
    fleet_id: int
    device_id: int
    sequence_id: int


def generate_records(config: GeneratorConfig) -> Iterator[GeneratedRecord]:
    rng = Random(config.seed)
    start_dt = _parse_start_time(config.start_time)
    interval_ms = _parse_rate_to_interval_ms(config.rate_of_emitting_dp)
    duration_ms = _parse_duration_ms(config.duration)
    end_dt = start_dt + timedelta(milliseconds=duration_ms)

    selected_dimensions = _parse_dimensions(config.dimensions)
    datapoint_count = config.number_of_dp
    sequence_id = 1

    fleet_base = rng.randint(1, 65000)
    for fleet_index in range(config.number_of_fleets):
        fleet_id = _normalize_uint16(fleet_base + fleet_index)
        device_base = rng.randint(1, 65000)
        device_ids = [
            _normalize_uint16(device_base + device_index)
            for device_index in range(config.number_of_devices_per_fleet)
        ]

        current_dt = start_dt
        while current_dt < end_dt:
            received_at = _format_iso_utc_ms(current_dt)
            for device_id in device_ids:
                header = _build_header(
                    rng,
                    fleet_id=fleet_id,
                    device_id=device_id,
                    sequence_id=sequence_id,
                    datapoint_count=datapoint_count,
                )
                datapoints = _build_datapoints(
                    rng,
                    datapoint_count=datapoint_count,
                    interval_ms=interval_ms,
                    selected_dimensions=selected_dimensions,
                )
                payload = encode_payload(header, datapoints)
                yield GeneratedRecord(
                    received_at=received_at,
                    payload=payload,
                    format_version=header.format_version,
                    fw_version=header.fw_version,
                    fleet_id=fleet_id,
                    device_id=device_id,
                    sequence_id=sequence_id,
                )
                sequence_id += 1
            current_dt += timedelta(milliseconds=interval_ms)


def _build_header(
    rng: Random,
    fleet_id: int,
    device_id: int,
    sequence_id: int,
    datapoint_count: int,
) -> PayloadHeader:
    return PayloadHeader(
        format_version=1,
        fw_version=1,
        fleet_id=fleet_id,
        device_id=device_id,
        sequence_id=sequence_id,
        battery_level_pct=rng.randint(20, 100),
        battery_health_pct=rng.randint(50, 100),
        solar_output_w=rng.uniform(0, 800),
        compute_util_pct=rng.randint(0, 100),
        compute_temp_c=rng.uniform(20, 90),
        charging_state=rng.randint(0, 1),
        signal_strength_dbm=rng.uniform(-120, -30),
    )


def _build_datapoints(
    rng: Random,
    datapoint_count: int,
    interval_ms: int,
    selected_dimensions: set[str],
) -> list[Datapoint]:
    step_ms = max(1, interval_ms // max(datapoint_count, 1))
    datapoints: list[Datapoint] = []
    for index in range(datapoint_count):
        sample_offset = min(index * step_ms, 65535)
        datapoints.append(
            Datapoint(
                sample_offset_ms=sample_offset,
                temperature_c=_value_or_zero(
                    rng.uniform(-20, 60), "temperature", selected_dimensions
                ),
                humidity_pct=_value_or_zero(
                    rng.uniform(0, 100), "humidity", selected_dimensions
                ),
                co2_ppm=_value_or_zero(
                    rng.uniform(350, 5000), "co2", selected_dimensions
                ),
                ozone_ppb=_value_or_zero(
                    rng.uniform(0, 500), "ozone", selected_dimensions
                ),
                nitrogen_dioxide_ppb=_value_or_zero(
                    rng.uniform(0, 200), "nitrogen_dioxide", selected_dimensions
                ),
                sulfur_dioxide_ppb=_value_or_zero(
                    rng.uniform(0, 200), "sulfur_dioxide", selected_dimensions
                ),
                pressure_hpa=_value_or_zero(
                    rng.uniform(900, 1100), "pressure", selected_dimensions
                ),
                solar_radiation_w_m2=_value_or_zero(
                    rng.uniform(0, 1500), "solar_radiation", selected_dimensions
                ),
                salinity_psu=_value_or_zero(
                    rng.uniform(0, 40), "salinity", selected_dimensions
                ),
                ph=_value_or_zero(rng.uniform(0, 14), "ph", selected_dimensions),
                dissolved_oxygen_mg_l=_value_or_zero(
                    rng.uniform(0, 20), "dissolved_oxygen", selected_dimensions
                ),
                turbidity_ntu=_value_or_zero(
                    rng.uniform(0, 500), "turbidity", selected_dimensions
                ),
                electrical_conductivity_us_cm=_value_or_zero(
                    rng.uniform(0, 50000),
                    "electrical_conductivity",
                    selected_dimensions,
                ),
                metals_ug_l=_value_or_zero(
                    rng.uniform(0, 1000), "metals", selected_dimensions
                ),
                plastic_particles_m3=_value_or_zero(
                    rng.uniform(0, 5000),
                    "plastic_particles",
                    selected_dimensions,
                ),
            )
        )
    return datapoints


def _parse_dimensions(value: str | list[str]) -> set[str]:
    if isinstance(value, str):
        if value == "all":
            return set(DIMENSION_IDS)
        if value.strip() == "":
            selected = set()
        else:
            selected = {item.strip() for item in value.split(",") if item.strip()}
    else:
        selected = set(value)

    unknown = sorted(selected.difference(DIMENSION_IDS))
    if unknown:
        raise ValueError(f"dimensions contains unknown values: {unknown}")
    return selected


def _value_or_zero(value: float, dimension: str, selected: set[str]) -> float:
    return value if dimension in selected else 0.0


def _parse_rate_to_interval_ms(rate: str) -> int:
    match = re.match(r"^\s*(\d+)\s+per\s+(second|minute|hour)\s*$", rate)
    if not match:
        raise ValueError(
            "rate_of_emitting_dp must match '<int> per <second|minute|hour>'"
        )
    count = int(match.group(1))
    unit = match.group(2)
    seconds = {"second": 1, "minute": 60, "hour": 3600}[unit]
    interval_seconds = seconds / max(count, 1)
    return max(1, int(round(interval_seconds * 1000)))


def _parse_duration_ms(duration: str) -> int:
    match = re.match(r"^\s*(\d+)\s+(second|minute|hour|day)s?\s*$", duration)
    if not match:
        raise ValueError("duration must match '<int> <second|minute|hour|day>'")
    count = int(match.group(1))
    unit = match.group(2)
    seconds = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[unit]
    return int(count * seconds * 1000)


def _parse_start_time(start_time: str | None) -> datetime:
    if not start_time:
        return datetime.now(timezone.utc)
    cleaned = start_time.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        raise ValueError("start_time must be UTC ISO-8601 with milliseconds")
    return parsed.astimezone(timezone.utc)


def _format_iso_utc_ms(value: datetime) -> str:
    value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _normalize_uint16(value: int) -> int:
    return ((value - 1) % 65535) + 1
