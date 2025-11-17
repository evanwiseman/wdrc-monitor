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

    def color(self) -> str:
        if self == State.UNKNOWN:
            return "gray"
        elif self == State.OFF:
            return "white"
        elif self == State.ON:
            return "green"
        elif self == State.FAULTED:
            return "red"
        elif self == State.BLUETOOTH:
            return "blue"
        elif self == State.NOT_TALKING:
            return "red"
        elif self == State.TALKING:
            return "green"
        else:
            return "gray"
