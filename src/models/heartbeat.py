from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class Heartbeat(QObject):
    timeout_signal = pyqtSignal()
    tick_signal = pyqtSignal(int)

    def __init__(self, name: str, retries_max: int, time_max: int) -> None:
        super().__init__()

        # Name of heartbeat
        self._name: str = name

        # Retries
        self._retry_attempt: int = 0
        self._retry_limit: int = retries_max

        # Time and Timers
        self._time: int = 0
        self._time_max: int = time_max

        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._update_timer)

        self._ping = -1

    @property
    def name(self) -> str:
        return self._name

    def _update_timer(self):
        """
        Update the timer, check if we've gone over time_max.
        If over time, heartbeat has expired and increment retries.
        Try again if retries are left.
        """
        # Update time and emit the new value
        self._time += 1
        self.tick_signal.emit(self._time)

        # Check if the timer has gone out of bounds
        if self._time >= self._time_max:
            self._retry_attempt += 1
            self._time = 0

        # Check if we've timed out
        if self._is_timeout():
            self.stop()
            self.timeout_signal.emit()

    def _update_ping(self, ping: int):
        """Update the ping number, expecting a high number every time"""
        if ping > self._ping:
            self._ping = ping
            self._time = 0
            self.stop()
            self.start()

    def _is_timeout(self):
        return self._retry_attempt > self._retry_limit

    def start(self):
        """Start the time to count 1 second, on expiration go to update_timer"""
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        """Stop the timer"""
        if self._timer.isActive():
            self._timer.stop()

    def reset(self):
        """Reset the heartbeat, clearing time and retries"""
        self._retry_attempt = 0
        self._time = 0
        self._ping = -1
        self.stop()

    def process(self, value: int):
        """Process a ping value"""
        if self._is_timeout():
            return
        self._update_ping(value)
