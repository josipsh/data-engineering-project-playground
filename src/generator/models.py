from dataclasses import dataclass


@dataclass
class DailyBounds:
    min_val: float
    max_val: float


@dataclass
class DeviceState:
    device_id: str
    battery_phase: float
    temperature_phase: float
    battery_bounds: DailyBounds
    temperature_bounds: DailyBounds


@dataclass
class SimRecord:
    record_number: int
    battery: float
    temperature: float


@dataclass
class DeviceOutput:
    device_id: str
    records: list[SimRecord]
