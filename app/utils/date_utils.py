from datetime import datetime


def current_utc_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
