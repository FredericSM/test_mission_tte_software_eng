# generate_data.py
from __future__ import annotations
from pathlib import Path
import csv
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = "Europe/Paris"
OUT = Path("sample_data")
random.seed(42)

def gen_regular_day(date_str: str, site_id: str, metric: str, freq_min: int = 15):
    """Generates a full day of points in local time (no DST edge assumed)."""
    tz = ZoneInfo(TZ)
    start = datetime.fromisoformat(f"{date_str}T00:00:00").replace(tzinfo=tz)
    rows = []
    t = start
    for _ in range(int(24 * 60 / freq_min)):
        val = 50 + 10 * random.random()
        rows.append((t.isoformat(), TZ, site_id, metric, f"{val:.3f}"))
        t += timedelta(minutes=freq_min)
    return rows

def gen_spring_forward_day(date_str: str, site_id: str, metric: str, freq_min: int = 15):
    """
    Creates local timestamps for the spring-forward day.
    In Europe/Paris, the local hour 02:00-02:59 does not exist.
    We intentionally write timestamps that include that hour to test your handling.
    """
    tz = ZoneInfo(TZ)
    start = datetime.fromisoformat(f"{date_str}T00:00:00").replace(tzinfo=tz)
    rows = []
    t = start
    for _ in range(int(24 * 60 / freq_min)):
        # Write local time as string; your pipeline will localize/normalize and must handle nonexistent times.
        val = 40 + 12 * random.random()
        rows.append((t.replace(tzinfo=None).isoformat(sep=" "), TZ, site_id, metric, f"{val:.3f}"))
        t += timedelta(minutes=freq_min)
    return rows

def gen_fall_back_day(date_str: str, site_id: str, metric: str, freq_min: int = 15):
    """
    Creates local timestamps for the fall-back day.
    The hour 02:00-02:59 occurs twice.
    We generate BOTH occurrences by adding a 'fold' column you can use to disambiguate (optional).
    """
    tz = ZoneInfo(TZ)
    # We'll create naive local times and include a fold indicator manually.
    start_naive = datetime.fromisoformat(f"{date_str}T00:00:00")
    rows = []
    t = start_naive
    for _ in range(int(24 * 60 / freq_min)):
        val = 60 + 8 * random.random()
        fold = "0"
        # Between 02:00 and 02:59, we duplicate entries to simulate repeated hour
        if t.hour == 2:
            # first occurrence
            rows.append((t.isoformat(sep=" "), TZ, site_id, metric, f"{val:.3f}", "0"))
            # second occurrence (fold=1)
            val2 = 60 + 8 * random.random()
            rows.append((t.isoformat(sep=" "), TZ, site_id, metric, f"{val2:.3f}", "1"))
        else:
            rows.append((t.isoformat(sep=" "), TZ, site_id, metric, f"{val:.3f}", fold))
        t += timedelta(minutes=freq_min)
    return rows

def write_csv(path: Path, header: list[str], rows: list[tuple]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def main():
    site_id = "FR001"
    metric = "power_mw"

    # Choose dates that correspond to DST changes in Europe/Paris (examples)
    # Spring forward: last Sunday of March (e.g. 2024-03-31)
    # Fall back: last Sunday of October (e.g. 2024-10-27)

    regular = gen_regular_day("2024-12-01", site_id, metric)
    write_csv(OUT / f"{site_id}_regular_2024-12-01.csv",
              ["ts", "tz", "site_id", "metric", "value"],
              regular)

    spring = gen_spring_forward_day("2024-03-31", site_id, metric)
    write_csv(OUT / f"{site_id}_dst_spring_2024-03-31.csv",
              ["ts", "tz", "site_id", "metric", "value"],
              spring)

    fall = gen_fall_back_day("2024-10-27", site_id, metric)
    write_csv(OUT / f"{site_id}_dst_fall_2024-10-27.csv",
              ["ts", "tz", "site_id", "metric", "value", "fold"],
              fall)

    print(f"Wrote files to: {OUT.resolve()}")

if __name__ == "__main__":
    main()