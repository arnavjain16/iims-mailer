"""
Give approved emails a send time (IST). The runner then sends them one per minute from that time
(hard rule: at least 60 s between any two emails), so 90 emails at 09:30 go out 09:30 -> ~11:00.

  python scripts/schedule_batch.py --at "2026-11-25 09:30"            only rows with no send_at yet
  python scripts/schedule_batch.py --at "2026-11-25 09:30" --all      every approved row
Then commit and push data/batch.csv.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import send  # noqa: E402
from scripts.runner import state as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--at", required=True, help='IST, e.g. "2026-11-25 09:30"')
ap.add_argument("--all", action="store_true")
a = ap.parse_args()
if S.parse_ist(a.at) is None:
    sys.exit('Use the form "YYYY-MM-DD HH:MM" (IST).')
rows = S.load_rows(send.BATCH)
n = 0
for r in rows:
    if r.get("status") == "approved" and (a.all or not r.get("send_at", "").strip()):
        r["send_at"] = a.at
        n += 1
S.save_rows(send.BATCH, rows, send.FIELDS)
print(f"{n} approved emails scheduled from {a.at} IST (one per minute, ~{n} minutes).")
