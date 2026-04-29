import math

from src.generator.models import DailyBounds


class SineGenerator:
    def compute(self, step: int, total_steps: int, bounds: DailyBounds, phase_offset: float) -> float:
        angle = (2 * math.pi * step / total_steps) + phase_offset
        normalized = (math.sin(angle) + 1) / 2
        value = bounds.min_val + normalized * (bounds.max_val - bounds.min_val)
        return round(value, 2)
