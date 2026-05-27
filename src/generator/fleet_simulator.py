import random

from src.generator.device_simulator import DeviceSimulator
from src.generator.models import DailyBounds, DeviceOutput, DeviceState
from src.generator.sine_generator import SineGenerator

_FLEET_PHASE_RANGE = 0.3
_DEVICE_PHASE_RANGE = 0.15

_BATTERY_MIN_RANGE = (0.0, 50.0)
_BATTERY_MAX_RANGE = (10.0, 100.0)
_BATTERY_MIN_SPREAD = 10.0

_TEMP_MIN_RANGE = (-10.0, 20.0)
_TEMP_MAX_RANGE = (-5.0, 45.0)
_TEMP_MIN_SPREAD = 5.0


def _random_bounds(min_range: tuple[float, float], max_range: tuple[float, float], min_spread: float) -> DailyBounds:
    min_val = random.uniform(*min_range)
    max_val = random.uniform(min_val + min_spread, max_range[1])
    return DailyBounds(min_val=round(min_val, 2), max_val=round(max_val, 2))


class FleetSimulator:
    def __init__(self, fleet_id: int, device_count: int, sine_generator: SineGenerator, total_steps: int) -> None:
        self._fleet_id = fleet_id
        self._device_count = device_count
        self._sine_generator = sine_generator
        self._total_steps = total_steps
        self._fleet_battery_phase = random.uniform(-_FLEET_PHASE_RANGE, _FLEET_PHASE_RANGE)
        self._fleet_temperature_phase = random.uniform(-_FLEET_PHASE_RANGE, _FLEET_PHASE_RANGE)

    def generate(self) -> list[DeviceOutput]:
        outputs: list[DeviceOutput] = []
        for device_index in range(self._device_count):
            device_id = f"fleet-{self._fleet_id}-device-{device_index + 1}"
            state = DeviceState(
                device_id=device_id,
                battery_phase=self._fleet_battery_phase + random.uniform(-_DEVICE_PHASE_RANGE, _DEVICE_PHASE_RANGE),
                temperature_phase=self._fleet_temperature_phase + random.uniform(-_DEVICE_PHASE_RANGE, _DEVICE_PHASE_RANGE),
                battery_bounds=_random_bounds(_BATTERY_MIN_RANGE, _BATTERY_MAX_RANGE, _BATTERY_MIN_SPREAD),
                temperature_bounds=_random_bounds(_TEMP_MIN_RANGE, _TEMP_MAX_RANGE, _TEMP_MIN_SPREAD),
            )
            simulator = DeviceSimulator(state, self._sine_generator, self._total_steps)
            outputs.append(simulator.generate())
        return outputs
