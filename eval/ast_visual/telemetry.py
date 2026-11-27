"""Summarize telemetry samples by channel."""

class Sample:
    """One timestamped reading from a channel."""

    def __init__(self, channel: str, value: float):
        self.channel = channel
        self.value = value

    def normalized(self, scale: float = 1.0) -> float:
        return self.value / scale


class SignalWindow:
    """Aggregate a moving window of signal readings."""

    def __init__(self, readings):
        self.readings = list(readings)

    def average(self) -> float:
        return mean_value(self.readings)

    def bounds(self) -> tuple:
        return min(self.readings), max(self.readings)


class SignalReport:
    """Produce a summary for the selected channel."""

    def collect(self, readings):
        return SignalWindow(readings)

    def describe(self, window) -> str:
        return str(window.bounds())

    async def publish(self, report):
        return report


def mean_value(values) -> float:
    """Calculate the arithmetic mean."""
    return sum(values) / len(values)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def group_channels(samples):
    def channel_key(sample):
        return sample.channel
    return sorted(samples, key=channel_key)
