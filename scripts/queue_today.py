"""
Daily queueing (run at 12 a.m. by a desktop scheduled task).

On a non-holiday weekday, gives up to DAILY_CAP approved, not-yet-scheduled emails a send time of
TODAY 08:30 IST and pushes data/batch.csv. The GitHub runner then sends them one per minute
(hard 60 s gap), so 90 emails go out 08:30 -> ~10:00, even with the laptop off.

Skips: Saturdays, Sundays, dates in data/holidays.txt, a day that already has emails queued,
and runs after 10:00 IST (too late for the morning window; use --force to override).

Works in a fresh temporary clone of the GitHub repo, so your local folder is never touched.

  python scripts/queue_today.py              normal (what the scheduled task runs)
  python scripts/queue_today.py --dry-run    show what it would queue; changes nothing
"""
import argparse
import subprocess
import sys
import tempfile
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

REPO = "arnavjain16/iims-mailer"
DAILY_CAP = 90
START = "08:30"
LATEST = time(10, 0)
IST = timezone(timedelta(hours=5, minutes=30))


def holidays(path):
    out = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line.split()[0])
    return out


def skip_reason(now, hol):
    day = now.strftime("%Y-%m-%d")
    if now.weekday() >= 5:
        return f"{day} is a {now.strftime('%A')}"
    if day in hol:
        return f"{day} is a holiday (data/holidays.txt)"
    return ""


def pick(rows, day, cap=DAILY_CAP):
    """Rows to queue for `day`: approved and unscheduled, in file order, at most cap minus already queued."""
    already = sum(1 for r in rows if (r.get("send_at") or "").startswith(day))
    free = [r for r in rows if r.get("status") == "approved" and not (r.get("send_at") or "").strip()]
    return free[: max(0, cap - already)], already


def run(*args, cwd):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"{args[0]} {args[1]} failed (exit {r.returncode})")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="queue even after 10:00 IST")
    a = ap.parse_args()
    now = datetime.now(IST)
    day = now.strftime("%Y-%m-%d")

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        run("gh", "repo", "clone", REPO, str(repo), "--", "-q", cwd=tmp)
        sys.path.insert(0, str(repo / "scripts"))
        sys.path.insert(0, str(repo))
        import send  # noqa: E402
        from scripts.runner import state as S  # noqa: E402

        reason = skip_reason(now, holidays(repo / "data" / "holidays.txt"))
        if reason:
            print(f"Nothing queued: {reason}.")
            return
        if now.time() > LATEST and not a.force:
            print(f"Nothing queued: it is {now:%H:%M} IST, after 10:00 (morning window is over).")
            return
        for attempt in range(3):
            rows = S.load_rows(repo / "data" / "batch.csv")
            chosen, already = pick(rows, day)
            if not chosen:
                print(f"Nothing new to queue for {day} ({already} already queued for today; "
                      f"{sum(r.get('status') == 'approved' and not r.get('send_at') for r in rows)} approved waiting).")
                return
            for r in chosen:
                r["send_at"] = f"{day} {START}"
            if a.dry_run:
                print(f"DRY RUN: would queue {len(chosen)} emails for {day} {START} IST:")
                for r in chosen:
                    print(f"  - {r['name']} ({r['institute']})")
                return
            S.save_rows(repo / "data" / "batch.csv", rows, send.FIELDS)
            run("git", "config", "user.name", "queue-task", cwd=repo)
            run("git", "config", "user.email", "queue-task@users.noreply.github.com", cwd=repo)
            run("git", "add", "data/batch.csv", cwd=repo)
            run("git", "commit", "-q", "-m", f"queue {day}: {len(chosen)} emails from {START} IST", cwd=repo)
            if subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=repo,
                              capture_output=True, timeout=180).returncode == 0:
                end = (datetime.strptime(f"{day} {START}", "%Y-%m-%d %H:%M") + timedelta(minutes=len(chosen) - 1))
                print(f"Queued {len(chosen)} emails for {day}, {START} to about {end:%H:%M} IST (one per minute).")
                return
            # the runner pushed meanwhile: start again from the latest version
            run("git", "fetch", "-q", "origin", "main", cwd=repo)
            run("git", "reset", "-q", "--hard", "origin/main", cwd=repo)
        sys.exit("Could not push after 3 tries; nothing queued. Try again.")


if __name__ == "__main__":
    main()
