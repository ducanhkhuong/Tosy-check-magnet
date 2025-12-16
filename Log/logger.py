import os
import time
from threading import Lock


class Logger:
    MAX_SIZE_BYTES = 3 * 1024 * 1024

    def __init__(self, logfile):
        self.logfile = logfile
        self.lock = Lock()

        log_dir = os.path.dirname(self.logfile)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        self._write("INFO", "Logger initialized")

    def _timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def _check_and_clean(self):
        if os.path.exists(self.logfile):
            size = os.path.getsize(self.logfile)
            if size > self.MAX_SIZE_BYTES:
                with open(self.logfile, "w", encoding="utf-8") as f:
                    f.write(
                        f"[{self._timestamp()}] [INFO] Log file cleaned (size exceeded 3MB)\n"
                    )

    def _write(self, level, message):
        with self.lock:
            self._check_and_clean()

            line = f"[{self._timestamp()}] [{level}] {message}\n"
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(line)

    def info(self, message):
        self._write("INFO", message)

    def warning(self, message):
        self._write("WARNING", message)

    def error(self, message):
        self._write("ERROR", message)

    def debug(self, message):
        self._write("DEBUG", message)
