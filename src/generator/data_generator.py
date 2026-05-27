from src.configs.config import Config
from src.configs.rate_enums import EmitRate
from src.generator.fleet_simulator import FleetSimulator
from src.generator.models import DeviceOutput
from src.generator.sine_generator import SineGenerator

_STEPS_PER_DAY: dict[EmitRate, int] = {
    EmitRate.ONE_PER_SECOND: 86400,
    EmitRate.TEN_PER_SECOND: 864000,
    EmitRate.ONE_PER_MINUTE: 1440,
    EmitRate.TEN_PER_MINUTE: 14400,
    EmitRate.ONE_PER_HOUR: 24,
    EmitRate.TEN_PER_HOUR: 240,
}


class DataGenerator:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._sine_generator = SineGenerator()
        self._total_steps = _STEPS_PER_DAY[config.rate_of_emitting_dp]

    def generate(self) -> list[DeviceOutput]:
        outputs: list[DeviceOutput] = []
        for fleet_index in range(self._config.number_of_fleets):
            fleet = FleetSimulator(
                fleet_id=fleet_index + 1,
                device_count=self._config.number_of_devices_per_fleet,
                sine_generator=self._sine_generator,
                total_steps=self._total_steps,
            )
            outputs.extend(fleet.generate())
        return outputs
