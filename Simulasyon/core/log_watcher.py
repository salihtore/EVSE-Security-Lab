# Simulasyon/core/log_watcher.py
import json
import os
import time
from typing import Generator

LOG_PATH = "alarms.json"


def read_alarms() -> list:
    if not os.path.exists(LOG_PATH):
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def tail_alarms(poll_interval: float = 1.0) -> Generator[dict, None, None]:
    """
    alarms.json dosyasına yeni alarm eklenirse yield eder
    """
    last_len = 0

    while True:
        alarms = read_alarms()

        if len(alarms) > last_len:
            for alarm in alarms[last_len:]:
                yield alarm

            last_len = len(alarms)

        time.sleep(poll_interval)
