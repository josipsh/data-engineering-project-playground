from src.generator.models import DeviceOutput, DeviceState, SimRecord
from src.generator.sine_generator import SineGenerator


class DeviceSimulator:
    def __init__(self, state: DeviceState, sine_generator: SineGenerator, total_steps: int) -> None:
        self._state = state
        self._sine_generator = sine_generator
        self._total_steps = total_steps

    def generate(self) -> DeviceOutput:
        records: list[SimRecord] = []
        for step in range(self._total_steps):
            battery = self._sine_generator.compute(
                step, self._total_steps, self._state.battery_bounds, self._state.battery_phase
            )
            temperature = self._sine_generator.compute(
                step, self._total_steps, self._state.temperature_bounds, self._state.temperature_phase
            )
            records.append(SimRecord(record_number=step + 1, battery=battery, temperature=temperature))
        return DeviceOutput(device_id=self._state.device_id, records=records)
