import os
from typing import List


def tail(filepath: str, n: int = 200) -> List[str]:
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return lines[-n:]
