from enum import Enum


class State(Enum):
    UNKNOWN = "Unknown"
    OFF = "Off"
    ON = "On"
    FAULTED = "Faulted"
    BLUETOOTH = "Bluetooth"
    NOT_TALKING = "Not Talking"
    TALKING = "Talking"

    def __str__(self):
        return self.value
