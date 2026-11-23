"""
State for the GitHub runner.

Queue  = data/batch.csv (one row per professor; see send.FIELDS).
         A row is DUE when status == "approved" and send_at (IST, "YYYY-MM-DD HH:MM") <= now.
Runner = data/runner_state.json: heartbeat, last send time, seen reply UIDs, halt flag.
         Only the runner writes it.

HARD RULE: at least MIN_GAP_SECONDS between any two emails, whatever the schedule says.
"""
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
MIN_GAP_SECONDS = 60
STAMP = "%Y-%m-%d %H:%M:%S"
# fields the RUNNER owns once it has acted on a row (sent / replied / failed)
RUNNER_FIELDS = ["sent_at", "message_id", "replied_at", "reply_from", "reply_note", "fail_reason"]
# when the laptop and the runner disagree about status, the "later" stage wins
STATUS_RANK = {"": 0, "draft": 1, "skip": 2, "approved": 2, "failed": 3, "sent": 4, "replied": 5}


def now_ist():
    return datetime.now(IST)


def parse_ist(text):
    """'2026-11-24 09:30' or '2026-11-24 09:30:05' (IST) -> aware datetime, or None."""
    text = (text or "").strip()
    for fmt in (STAMP, "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=IST)
        except ValueError:
            pass
    return None


def stamp(dt):
    return dt.astimezone(IST).strftime(STAMP)


# ---------------------------------------------------------------- queue file
def load_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save_rows(path, rows, fields):
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


# ---------------------------------------------------------------- runner state file
def default_state():
    return {"last_loop_at": "", "last_sent_at": "", "halted": "", "gap_reported_for": "",
            "uidvalidity": "", "seen_uids": [], "last_real_send_at": ""}


def load_state(path):
    path = Path(path)
    st = default_state()
    if path.exists():
        try:
            st.update(json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            pass
    return st


def save_state(path, st):
    Path(path).write_text(json.dumps(st, indent=1, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- send-time rules
def is_due(row, now):
    if row.get("status", "").strip() != "approved":
        return False
    at = parse_ist(row.get("send_at"))
    return at is not None and at <= now


def last_send_time(rows, st):
    """Latest moment ANY email went out (rows' sent_at or the runner's own record)."""
    times = [parse_ist(r.get("sent_at")) for r in rows] + [parse_ist(st.get("last_sent_at"))]
    times = [t for t in times if t]
    return max(times) if times else None


def gap_ok(last_sent, now, gap=MIN_GAP_SECONDS):
    return last_sent is None or (now - last_sent).total_seconds() >= gap


def next_due(rows, now):
    """The single due row to send now: earliest send_at first, then file order."""
    due = [(parse_ist(r["send_at"]), i, r) for i, r in enumerate(rows) if is_due(r, now)]
    return min(due)[2] if due else None


# ---------------------------------------------------------------- conflict reconcile
def _acted(row):
    return bool((row.get("sent_at") or "").strip()) or row.get("status") in ("sent", "replied", "failed")


def reconcile(runner_rows, origin_rows):
    """
    Merge after a rejected push.
    - origin_rows (laptop's latest) decide order, new rows, and everything the runner has not acted on.
    - For rows the runner sent / saw a reply for / marked failed: keep the runner's send+reply fields,
      and the later of the two statuses (so a laptop 'replied' mark is not lost either).
    - A row the runner already sent is never dropped, even if the laptop deleted it.
    """
    mine = {r["email"].strip().lower(): r for r in runner_rows if r.get("email")}
    seen, out = set(), []
    for o in origin_rows:
        key = o.get("email", "").strip().lower()
        merged = dict(o)
        r = mine.get(key)
        if r and _acted(r):
            for f in RUNNER_FIELDS:
                if (r.get(f) or "").strip():
                    merged[f] = r[f]
            a, b = r.get("status", ""), o.get("status", "")
            merged["status"] = a if STATUS_RANK.get(a, 0) >= STATUS_RANK.get(b, 0) else b
        out.append(merged)
        seen.add(key)
    for key, r in mine.items():
        if key not in seen and _acted(r):
            out.append(r)
    return out
