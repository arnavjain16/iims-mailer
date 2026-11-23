"""
GitHub Actions runner: one run lives ~5 h 40 min and loops every LOOP_SECONDS.

Each loop:
  1. git pull + reload data/batch.csv (so batches queued from the laptop are picked up)
  2. send AT MOST ONE due email, and only if >= 60 s have passed since the last email (hard rule)
  3. check the inbox (IMAP, read-only) for replies -> one GitHub Issue each
  4. save state, commit and push (record-level reconcile if the push is rejected)
Near the end it starts its successor (self-chaining) while anything is scheduled,
or for 30 days after the last real send so replies keep being picked up.

Real sending only when SENDING_ENABLED=true (repo variable) - the kill switch.
DRY_RUN_TO set: the first DRY_RUN_LIMIT approved rows (send_at ignored) go to that address instead,
nothing is marked sent, nothing is committed, no Issues are opened, and the run ends.

Run locally (tests use fakes):  python scripts/runner/tick.py --max-minutes 3
"""
import argparse
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))            # scripts/ -> import send
sys.path.insert(0, str(HERE.parent.parent))     # repo root -> import scripts.runner.*

import send  # noqa: E402
from scripts.runner import state as S  # noqa: E402

ROOT = HERE.parent.parent
BATCH = ROOT / "data" / "batch.csv"
STATE = ROOT / "data" / "runner_state.json"
LOOP_SECONDS = 60
RUN_SECONDS = 5 * 3600 + 40 * 60
CHAIN_MARGIN = 3 * 60          # start the successor this long before the end
GAP_ALERT = timedelta(minutes=40)
KEEP_ALIVE = timedelta(days=30)
MAX_TRANSIENT = 5              # consecutive network errors before halting


def log(msg):
    print(f"[{S.stamp(S.now_ist())}] {msg}", flush=True)


class Runner:
    """All side effects come in through deps, so tests can drive it with fakes."""

    def __init__(self, deps, cfg):
        self.d, self.c = deps, cfg
        self.transient = 0
        self.dry_done = set()

    # -------------------------------------------------- one loop
    def iteration(self):
        d, c = self.d, self.c
        now = d.clock.now()
        if not c.dry_run_to:
            try:
                d.git.pull()
            except Exception as e:
                log(f"git pull error: {type(e).__name__}")
        rows = d.store.load_rows()
        st = d.store.load_state()
        changed = False

        # heartbeat + gap alert (> 40 min without a loop)
        last_loop = S.parse_ist(st.get("last_loop_at"))
        if not c.dry_run_to and last_loop and now - last_loop > GAP_ALERT and st.get("gap_reported_for") != st["last_loop_at"]:
            mins = int((now - last_loop).total_seconds() // 60)
            if d.issues.create(f"Runner gap: no loop for {mins} min",
                               f"Last loop {st['last_loop_at']} IST, resumed {S.stamp(now)} IST. "
                               "Scheduled emails due in that window go out now, one per minute.", "needs-attention"):
                st["gap_reported_for"] = st["last_loop_at"]
        st["last_loop_at"] = S.stamp(now)

        # ---- send at most one email
        if st.get("halted"):
            log(f"sending halted: {st['halted']} (clear 'halted' in data/runner_state.json to resume)")
        elif c.dry_run_to:
            changed |= self._dry_send(rows, st, now)
        elif c.sending_enabled:
            changed |= self._real_send(rows, st, now)

        # ---- replies
        if not c.dry_run_to:
            changed |= self._replies(rows, st)

        # ---- save + push
        d.store.save_rows(rows)
        d.store.save_state(st)
        if not c.dry_run_to:
            try:
                d.git.commit_push(f"runner {S.stamp(now)} IST", d.store.read_both,
                                  d.store.write_both, lambda mine: S.reconcile(mine, d.store.load_rows()))
            except Exception as e:
                log(f"git push error: {type(e).__name__}")
        return changed

    def _real_send(self, rows, st, now):
        d, c = self.d, self.c
        row = S.next_due(rows, now)
        if row is None:
            return False
        last = S.last_send_time(rows, st)
        if not S.gap_ok(last, now):
            return False                                   # HARD RULE: wait for the 60 s gap
        try:
            mid = d.mailer.send(row, to=row["email"], bcc=c.sender_email)
        except d.errors.AuthFailed as e:
            st["halted"] = f"login failed ({e}) {S.stamp(now)}"
            d.issues.create("Sending stopped: IITB login failed",
                            f"The mail server rejected the login ({e}). No more emails will be sent. "
                            "Renew the SSO token in the SENDER_APP_TOKEN secret, then clear 'halted' "
                            "in data/runner_state.json.", "needs-attention")
            log(f"login failed: {e}")
            return True
        except d.errors.Rejected as e:
            row["status"], row["fail_reason"] = "failed", f"SMTP {e.code}"
            st["halted"] = f"SMTP {e.code} on {row['email']} {S.stamp(now)}"
            d.issues.create(f"Sending stopped: SMTP {e.code} for {row['name']}",
                            f"The server rejected the email to {row['email']} with code {e.code}. "
                            "That row is marked failed and sending is stopped (no retries). "
                            "Clear 'halted' in data/runner_state.json to resume.", "needs-attention")
            log(f"SMTP rejection {e.code}")
            return True
        except d.errors.Transient as e:
            self.transient += 1
            log(f"network error {e} ({self.transient}/{MAX_TRANSIENT}); will try next minute")
            if self.transient >= MAX_TRANSIENT:
                st["halted"] = f"{MAX_TRANSIENT} network errors in a row {S.stamp(now)}"
                d.issues.create("Sending stopped: repeated network errors",
                                f"{MAX_TRANSIENT} sends in a row failed to connect ({e}).", "needs-attention")
            return False
        self.transient = 0
        sent_at = S.stamp(d.clock.now())
        row.update(status="sent", sent_at=sent_at, message_id=mid)
        st["last_sent_at"] = st["last_real_send_at"] = sent_at
        log(f"sent {row['name']} ({row['institute']})")
        return True

    def _dry_send(self, rows, st, now):
        d, c = self.d, self.c
        if len(self.dry_done) >= c.dry_run_limit:
            return False
        last = S.parse_ist(st.get("last_sent_at"))
        if not S.gap_ok(last, now):
            return False
        row = next((r for r in rows if r.get("status") == "approved" and r["email"] not in self.dry_done), None)
        if row is None:
            return False
        try:
            d.mailer.send(row, to=c.dry_run_to, bcc=None)
        except Exception as e:
            log(f"dry-run send error: {getattr(e, 'code', type(e).__name__)}")
            self.dry_done.add(row["email"])
            return False
        self.dry_done.add(row["email"])
        st["last_sent_at"] = S.stamp(d.clock.now())       # gap rule applies to dry runs too
        log(f"DRY RUN: {row['name']}'s email sent to the test address")
        return False                                       # nothing to commit in a dry run

    def _replies(self, rows, st):
        d = self.d
        try:
            uv, found = d.replies.poll(rows, st)
        except Exception as e:
            log(f"IMAP error: {type(e).__name__}")
            return False
        if uv != st.get("uidvalidity"):
            st["uidvalidity"], st["seen_uids"] = uv, []
        seen = set(st["seen_uids"])
        changed = False
        for m in found:
            if m["row"] is None:
                seen.add(m["uid"])
                continue
            r = m["row"]
            body = (f"**From:** {m['from']}\n**Professor:** {r['name']} ({r['institute']})\n"
                    f"**Subject:** {m['subject']}\n\n> {m['excerpt']}")
            if d.issues.create(f"Reply: {r['name']} ({r['institute']})", body, "reply"):
                seen.add(m["uid"])                      # seen ONLY after its Issue exists
                r.update(status="replied", replied_at=S.stamp(d.clock.now()), reply_from=m["from"],
                         reply_note=m["subject"][:120])
                changed = True
        st["seen_uids"] = sorted(seen)
        return changed

    # -------------------------------------------------- whole run
    def keep_alive(self):
        rows, st = self.d.store.load_rows(), self.d.store.load_state()
        if any(r.get("status") == "approved" for r in rows):
            return True
        last = S.parse_ist(st.get("last_real_send_at"))
        return bool(last and self.d.clock.now() - last < KEEP_ALIVE)

    def run(self, run_seconds=RUN_SECONDS):
        d, c = self.d, self.c
        start = d.clock.monotonic()
        chained = False
        if not c.dry_run_to and not self.keep_alive():
            log("nothing scheduled and no send in the last 30 days: one check, then exit")
            try:
                self.iteration()
            except Exception as e:
                log(f"loop error: {type(e).__name__}")
            d.mailer.close()
            d.replies.close()
            return
        while True:
            elapsed = d.clock.monotonic() - start
            if elapsed >= run_seconds:
                break
            try:
                self.iteration()
            except Exception as e:                       # never crash the loop
                log(f"loop error: {type(e).__name__}")
            if c.dry_run_to and (len(self.dry_done) >= c.dry_run_limit or
                                 not any(r.get("status") == "approved" and r["email"] not in self.dry_done
                                         for r in d.store.load_rows())):
                log("dry run finished")
                break
            if not c.dry_run_to and not chained and elapsed >= run_seconds - CHAIN_MARGIN:
                if self.keep_alive():
                    d.chain()
                    log("successor run started")
                chained = True
            d.clock.sleep(LOOP_SECONDS)
        d.mailer.close()
        d.replies.close()


# ====================================================== real wiring
class Clock:
    now = staticmethod(S.now_ist)
    monotonic = staticmethod(time.monotonic)
    sleep = staticmethod(time.sleep)


class Store:
    def load_rows(self):
        return S.load_rows(BATCH)

    def save_rows(self, rows):
        S.save_rows(BATCH, rows, send.FIELDS)

    def load_state(self):
        return S.load_state(STATE)

    def save_state(self, st):
        S.save_state(STATE, st)

    def read_both(self):
        return self.load_rows(), self.load_state()

    def write_both(self, rows, st):
        self.save_rows(rows)
        self.save_state(st)


class Deps:
    pass


class Cfg:
    pass


def main():
    from scripts.runner import adapters as A
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-minutes", type=float, default=RUN_SECONDS / 60)
    args = ap.parse_args()

    user, token = send.credentials()
    sender_email = send.FROM_ADDR
    if not user or not token:
        sys.exit("SMTP_USER / SENDER_APP_TOKEN are not set.")
    c = Cfg()
    c.dry_run_to = os.environ.get("DRY_RUN_TO", "").strip()
    c.dry_run_limit = int(os.environ.get("DRY_RUN_LIMIT", "2") or 2)
    c.sending_enabled = os.environ.get("SENDING_ENABLED", "").strip().lower() == "true"
    c.sender_email = sender_email
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    d = Deps()
    d.clock, d.store, d.errors = Clock(), Store(), A
    d.mailer = A.Mailer(user, token)
    d.replies = A.Replies(user, token, sender_email)
    d.git = A.Git(["data/batch.csv", "data/runner_state.json"])
    try:
        d.issues = A.Issues(repo)
    except Exception as e:
        log(f"issues setup error: {type(e).__name__}")
        d.issues = A.Issues.__new__(A.Issues)
        d.issues.repo = repo

    def chain():
        import subprocess
        r = subprocess.run(["gh", "workflow", "run", "tick.yml", "--ref", "main", "-R", repo],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            log(f"chain error: gh exit {r.returncode}")
    d.chain = chain

    log(f"start: {'DRY RUN to test address' if c.dry_run_to else ('sending ON' if c.sending_enabled else 'sending OFF (kill switch)')}")
    Runner(d, c).run(int(args.max_minutes * 60))


if __name__ == "__main__":
    main()
