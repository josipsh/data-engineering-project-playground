from __future__ import annotations

import base64
import struct
from dataclasses import dataclass
from typing import Iterable


HEADER_SIZE_BYTES = 21
DATAPOINT_SIZE_BYTES = 32
CRC_SIZE_BYTES = 2

_HEADER_STRUCT = struct.Struct(">BBHHIBBHBhBhB")
_DATAPOINT_STRUCT = struct.Struct(">Hh" + "H" * 14)


SCALES = {
    "solar_output_w": 0.1,
    "compute_temp_c": 0.1,
    "signal_strength_dbm": 0.1,
    "temperature_c": 0.1,
    "humidity_pct": 0.1,
    "co2_ppm": 1.0,
    "ozone_ppb": 1.0,
    "nitrogen_dioxide_ppb": 1.0,
    "sulfur_dioxide_ppb": 1.0,
    "pressure_hpa": 0.1,
    "solar_radiation_w_m2": 1.0,
    "salinity_psu": 0.01,
    "ph": 0.01,
    "dissolved_oxygen_mg_l": 0.01,
    "turbidity_ntu": 0.01,
    "electrical_conductivity_us_cm": 1.0,
    "metals_ug_l": 1.0,
    "plastic_particles_m3": 1.0,
}


@dataclass(frozen=True)
class PayloadHeader:
    format_version: int
    fw_version: int
    fleet_id: int
    device_id: int
    sequence_id: int
    battery_level_pct: int
    battery_health_pct: int
    solar_output_w: float
    compute_util_pct: int
    compute_temp_c: float
    charging_state: int
    signal_strength_dbm: float


@dataclass(frozen=True)
class Datapoint:
    sample_offset_ms: int
    temperature_c: float
    humidity_pct: float
    co2_ppm: float
    ozone_ppb: float
    nitrogen_dioxide_ppb: float
    sulfur_dioxide_ppb: float
    pressure_hpa: float
    solar_radiation_w_m2: float
    salinity_psu: float
    ph: float
    dissolved_oxygen_mg_l: float
    turbidity_ntu: float
    electrical_conductivity_us_cm: float
    metals_ug_l: float
    plastic_particles_m3: float


def encode_payload(header: PayloadHeader, datapoints: Iterable[Datapoint]) -> bytes:
    datapoint_list = list(datapoints)
    payload = bytearray()
    payload.extend(_encode_header(header, len(datapoint_list)))
    for datapoint in datapoint_list:
        payload.extend(_encode_datapoint(datapoint))
    crc = crc16_ccitt_false(bytes(payload))
    payload.extend(struct.pack(">H", crc))
    return bytes(payload)


def encode_payload_base64(
    header: PayloadHeader, datapoints: Iterable[Datapoint]
) -> str:
    payload_bytes = encode_payload(header, datapoints)
    return base64.b64encode(payload_bytes).decode("ascii")


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def _encode_header(header: PayloadHeader, datapoint_count: int) -> bytes:
    _check_uint8(header.format_version, "format_version")
    _check_uint8(header.fw_version, "fw_version")
    _check_uint16(header.fleet_id, "fleet_id")
    _check_uint16(header.device_id, "device_id")
    _check_uint32(header.sequence_id, "sequence_id")
    _check_uint8(header.battery_level_pct, "battery_level_pct")
    _check_uint8(header.battery_health_pct, "battery_health_pct")
    _check_uint8(header.compute_util_pct, "compute_util_pct")
    _check_uint8(header.charging_state, "charging_state")
    _check_uint8(datapoint_count, "datapoint_count")

    solar_output_raw = _scale_to_int(header.solar_output_w, "solar_output_w")
    compute_temp_raw = _scale_to_int(header.compute_temp_c, "compute_temp_c")
    signal_strength_raw = _scale_to_int(
        header.signal_strength_dbm, "signal_strength_dbm"
    )

    _check_uint16(solar_output_raw, "solar_output_w")
    _check_int16(compute_temp_raw, "compute_temp_c")
    _check_int16(signal_strength_raw, "signal_strength_dbm")

    return _HEADER_STRUCT.pack(
        header.format_version,
        header.fw_version,
        header.fleet_id,
        header.device_id,
        header.sequence_id,
        header.battery_level_pct,
        header.battery_health_pct,
        solar_output_raw,
        header.compute_util_pct,
        compute_temp_raw,
        header.charging_state,
        signal_strength_raw,
        datapoint_count,
    )


def _encode_datapoint(datapoint: Datapoint) -> bytes:
    _check_uint16(datapoint.sample_offset_ms, "sample_offset_ms")
    temp_raw = _scale_to_int(datapoint.temperature_c, "temperature_c")
    humidity_raw = _scale_to_int(datapoint.humidity_pct, "humidity_pct")
    co2_raw = _scale_to_int(datapoint.co2_ppm, "co2_ppm")
    ozone_raw = _scale_to_int(datapoint.ozone_ppb, "ozone_ppb")
    no2_raw = _scale_to_int(datapoint.nitrogen_dioxide_ppb, "nitrogen_dioxide_ppb")
    so2_raw = _scale_to_int(datapoint.sulfur_dioxide_ppb, "sulfur_dioxide_ppb")
    pressure_raw = _scale_to_int(datapoint.pressure_hpa, "pressure_hpa")
    solar_raw = _scale_to_int(datapoint.solar_radiation_w_m2, "solar_radiation_w_m2")
    salinity_raw = _scale_to_int(datapoint.salinity_psu, "salinity_psu")
    ph_raw = _scale_to_int(datapoint.ph, "ph")
    oxygen_raw = _scale_to_int(datapoint.dissolved_oxygen_mg_l, "dissolved_oxygen_mg_l")
    turbidity_raw = _scale_to_int(datapoint.turbidity_ntu, "turbidity_ntu")
    conductivity_raw = _scale_to_int(
        datapoint.electrical_conductivity_us_cm, "electrical_conductivity_us_cm"
    )
    metals_raw = _scale_to_int(datapoint.metals_ug_l, "metals_ug_l")
    plastic_raw = _scale_to_int(datapoint.plastic_particles_m3, "plastic_particles_m3")

    _check_int16(temp_raw, "temperature_c")
    _check_uint16(humidity_raw, "humidity_pct")
    _check_uint16(co2_raw, "co2_ppm")
    _check_uint16(ozone_raw, "ozone_ppb")
    _check_uint16(no2_raw, "nitrogen_dioxide_ppb")
    _check_uint16(so2_raw, "sulfur_dioxide_ppb")
    _check_uint16(pressure_raw, "pressure_hpa")
    _check_uint16(solar_raw, "solar_radiation_w_m2")
    _check_uint16(salinity_raw, "salinity_psu")
    _check_uint16(ph_raw, "ph")
    _check_uint16(oxygen_raw, "dissolved_oxygen_mg_l")
    _check_uint16(turbidity_raw, "turbidity_ntu")
    _check_uint16(conductivity_raw, "electrical_conductivity_us_cm")
    _check_uint16(metals_raw, "metals_ug_l")
    _check_uint16(plastic_raw, "plastic_particles_m3")

    return _DATAPOINT_STRUCT.pack(
        datapoint.sample_offset_ms,
        temp_raw,
        humidity_raw,
        co2_raw,
        ozone_raw,
        no2_raw,
        so2_raw,
        pressure_raw,
        solar_raw,
        salinity_raw,
        ph_raw,
        oxygen_raw,
        turbidity_raw,
        conductivity_raw,
        metals_raw,
        plastic_raw,
    )


def _scale_to_int(value: float, field: str) -> int:
    scale = SCALES.get(field, 1.0)
    return int(round(value / scale))


def _check_uint8(value: int, field: str) -> None:
    if not 0 <= value <= 0xFF:
        raise ValueError(f"{field} out of range for uint8: {value}")


def _check_uint16(value: int, field: str) -> None:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(f"{field} out of range for uint16: {value}")


def _check_uint32(value: int, field: str) -> None:
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError(f"{field} out of range for uint32: {value}")


def _check_int16(value: int, field: str) -> None:
    if not -0x8000 <= value <= 0x7FFF:
        raise ValueError(f"{field} out of range for int16: {value}")
