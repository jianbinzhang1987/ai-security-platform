from __future__ import annotations

import random


class SamplingProcessor:
    def __init__(self, sampling_rate: float = 1.0):
        self.sampling_rate = sampling_rate

    def should_sample(self, span) -> bool:
        if self.sampling_rate >= 1.0:
            return True
        if self.sampling_rate <= 0.0:
            return False
        return random.random() <= self.sampling_rate
