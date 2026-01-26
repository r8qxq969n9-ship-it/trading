import csv
import time
from pathlib import Path
from typing import List

import requests

KRX_SOURCE = "https://raw.githubusercontent.com/FinanceData/FinanceDataReader/master/FinanceDataReader/data/krx/krx_code.csv"
DEFAULT_PATH = Path("data/krx_universe.csv")
DEFAULT_TTL = 60 * 60 * 24  # 24 hours


def ensure_universe_csv(path: Path = DEFAULT_PATH, ttl: int = DEFAULT_TTL) -> Path:
    """
    Download KRX symbol list if missing or stale.
    Source: FinanceDataReader public GitHub (krx_code.csv).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        mtime = path.stat().st_mtime
        if time.time() - mtime < ttl:
            return path

    resp = requests.get(KRX_SOURCE, timeout=10)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return path


def load_universe(limit: int = 200) -> List[str]:
    """
    Return a list of KRX tickers (zero-padded 6 digits).
    Limit to avoid overloading API calls.
    """
    path = ensure_universe_csv()
    symbols: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Code") or row.get("code")
            if code:
                symbols.append(code.strip())
            if len(symbols) >= limit:
                break
    return symbols
