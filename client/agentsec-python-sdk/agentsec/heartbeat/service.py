import threading
import time

class HeartbeatService:
    def __init__(self, interval=30):
        self.interval = interval
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while True:
            # Send heartbeat
            time.sleep(self.interval)
