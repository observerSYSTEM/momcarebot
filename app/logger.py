from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime
from typing import Optional

LOG_PATH = Path("data/logs.csv")


def log_event(job: str, status: str, message: str = "", extra: str = "") -> None:
    """
    Append a log line to data/logs.csv.

    Columns:
      timestamp_uk, job, status, message, extra

    status examples: STARTED, SENT, ERROR
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp_uk": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "job": job,
        "status": status,
        "message": (message or "")[:400],  # avoid huge logs
        "extra": (extra or "")[:400],
    }

    file_exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp_uk", "job", "status", "message", "extra"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
