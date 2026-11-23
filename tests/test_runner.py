"""
Tests for the GitHub runner: send-time check, the 60-second hard rule, the loop, and the conflict reconcile.
Everything external (SMTP, IMAP, git, Issues, clock) is faked; nothing is sent.

  python -m pytest -q tests
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from scripts.runner import state as S  # noqa: E402
from scripts.runner import tick as T  # noqa: E402
from scripts.runner import adapters as A  # noqa: E402

IST = S.IST


def at(hm, day="2026-11-24"):
    return datetime.strptime(f"{day} {hm}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)


def row(email, status="approved", send_at="2026-11-24 09:30", **kw):
    r = {"name": email.split("@")[0], "surname": "X", "institute": "IIM A", "email": email, "field": "A",
         "subject_topic": "Topic", "opening_line": "Line.", "quant_line": "", "profile_url": "u",
         "status": status, "sent_at": "", "message_id": "", "send_at": send_at,
         "replied_at": "", "reply_from": "", "reply_note": "", "fail_reason": ""}
    r.update(kw)
    return r


# ------------------------------------------------------------------ fakes
class FakeClock:
    def __init__(self, start):
        self.t = start
        self.mono = 0.0

    def now(self):
        return self.t

    def monotonic(self):
        return self.mono

    def sleep(self, s):
        self.t += timedelta(seconds=s)
        self.mono += s


class FakeStore:
    def __init__(self, rows, st=None, enabled=True):
        self.rows, self.st, self.enabled = rows, st or S.default_state(), enabled

    def sending_enabled(self):
        return self.enabled

    def load_rows(self):
        return [dict(r) for r in self.rows]

    def save_rows(self, rows):
        self.rows = [dict(r) for r in rows]

    def load_state(self):
        return dict(self.st)

    def save_state(self, st):
        self.st = dict(st)

    def read_both(self):
        return self.load_rows(), self.load_state()

    def write_both(self, rows, st):
        self.save_rows(rows)
        self.save_state(st)


class FakeMailer:
    def __init__(self, clock, fail=None):
        self.clock, self.fail, self.sent = clock, fail, []

    def send(self, row, to, bcc):
        if self.fail:
            raise self.fail
        self.sent.append((to, row["email"], self.clock.now()))
        return f"<{len(self.sent)}@test>"

    def close(self):
        pass


class FakeReplies:
    def __init__(self, found=None, error=None):
        self.found, self.error = found or [], error

    def poll(self, rows, st):
        if self.error:
            raise self.error
        out = []
        for f in self.found:
            r = next(x for x in rows if x["email"] == f["email"]) if f.get("email") else None
            out.append({"uid": f["uid"], "row": r, "from": f.get("email", ""), "subject": "Re: hi", "excerpt": "Yes"})
        return "1", out

    def close(self):
        pass


class FakeIssues:
    def __init__(self, ok=True):
        self.ok, self.made = ok, []

    def create(self, title, body, label):
        if self.ok:
            self.made.append((title, label))
        return self.ok


class FakeGit:
    def __init__(self):
        self.pushes = 0

    def pull(self):
        pass

    def commit_push(self, message, read_mine, write_merged, reconcile_fn):
        self.pushes += 1
        return True


def make(rows, start, sending=True, dry=None, mail_fail=None, replies=None, issues_ok=True, st=None):
    clock = FakeClock(start)
    d = T.Deps()
    d.clock, d.store, d.errors = clock, FakeStore(rows, st, enabled=sending), A
    d.mailer = FakeMailer(clock, mail_fail)
    d.replies = replies or FakeReplies()
    d.issues, d.git = FakeIssues(issues_ok), FakeGit()
    d.chained = 0

    def chain():
        d.chained += 1
    d.chain = chain
    c = T.Cfg()
    c.dry_run_to, c.dry_run_limit, c.sender_email = dry or "", 2, "me@iitb.ac.in"
    return T.Runner(d, c), d


# ------------------------------------------------------------------ send-time check
def test_due_only_when_approved_and_time_has_come():
    assert not S.is_due(row("a@x"), at("09:29"))
    assert S.is_due(row("a@x"), at("09:30"))
    assert not S.is_due(row("a@x", status="draft"), at("10:00"))
    assert not S.is_due(row("a@x", status="sent"), at("10:00"))
    assert not S.is_due(row("a@x", send_at=""), at("10:00"))


def test_gap_rule():
    assert S.gap_ok(None, at("09:30"))
    assert not S.gap_ok(at("09:30"), at("09:30") + timedelta(seconds=59))
    assert S.gap_ok(at("09:30"), at("09:31"))


def test_next_due_is_earliest_then_file_order():
    rows = [row("b@x", send_at="2026-11-24 09:31"), row("a@x"), row("c@x")]
    assert S.next_due(rows, at("10:00"))["email"] == "a@x"


# ------------------------------------------------------------------ the loop
def test_90_due_at_930_go_out_one_per_minute_until_1100():
    rows = [row(f"p{i}@x") for i in range(90)]
    r, d = make(rows, at("09:29"))
    r.run(run_seconds=100 * 60)
    times = [t for _, _, t in d.mailer.sent]
    assert len(times) == 90
    assert times[0] == at("09:30")
    assert all((b - a).total_seconds() >= 60 for a, b in zip(times, times[1:]))   # HARD RULE
    assert times[-1] <= at("11:00")
    assert all(x["status"] == "sent" and x["message_id"] for x in d.store.rows)


def test_gap_counts_previous_sends_from_another_run():
    rows = [row("a@x", status="sent", sent_at="2026-11-24 09:30:30"), row("b@x")]
    r, d = make(rows, at("09:31"))       # only 30 s after the last send
    r.iteration()
    assert d.mailer.sent == []
    d.clock.sleep(60)
    r.iteration()
    assert len(d.mailer.sent) == 1


def test_kill_switch_off_sends_nothing_and_is_read_live():
    r, d = make([row("a@x")], at("10:00"), sending=False)
    r.iteration()
    assert d.mailer.sent == []
    d.store.enabled = True                # flipped while the run is going
    d.clock.sleep(60)
    r.iteration()
    assert len(d.mailer.sent) == 1


def test_smtp_rejection_marks_failed_halts_and_opens_issue():
    r, d = make([row("a@x"), row("b@x")], at("10:00"), mail_fail=A.Rejected(550))
    r.iteration()
    assert d.store.rows[0]["status"] == "failed" and d.store.rows[0]["fail_reason"] == "SMTP 550"
    assert d.store.st["halted"]
    assert d.issues.made[0][1] == "needs-attention"
    d.mailer.fail = None
    d.clock.sleep(60)
    r.iteration()                         # halted: no retry, nothing else sent
    assert d.mailer.sent == []


def test_login_failure_halts():
    r, d = make([row("a@x")], at("10:00"), mail_fail=A.AuthFailed("SMTP 535"))
    r.iteration()
    assert "login failed" in d.store.st["halted"]
    assert d.store.rows[0]["status"] == "approved"


def test_reply_marked_seen_only_after_issue_exists():
    rows = [row("a@x", status="sent", sent_at="2026-11-24 09:30:00", message_id="<m1>")]
    r, d = make(rows, at("12:00"), replies=FakeReplies([{"uid": 7, "email": "a@x"}]), issues_ok=False)
    r.iteration()
    assert 7 not in d.store.st["seen_uids"] and d.store.rows[0]["status"] == "sent"
    d.issues.ok = True
    r.iteration()
    assert 7 in d.store.st["seen_uids"] and d.store.rows[0]["status"] == "replied"
    assert d.issues.made[-1][1] == "reply"


def test_imap_error_is_logged_not_fatal():
    r, d = make([row("a@x")], at("10:00"), replies=FakeReplies(error=OSError()))
    r.iteration()
    assert len(d.mailer.sent) == 1


def test_gap_alert_after_40_minutes():
    st = S.default_state()
    st["last_loop_at"] = "2026-11-24 09:00:00"
    r, d = make([], at("09:45"), st=st)
    r.iteration()
    assert any(lbl == "needs-attention" and "gap" in t.lower() for t, lbl in d.issues.made)
    n = len(d.issues.made)
    d.store.st["last_loop_at"] = "2026-11-24 09:00:00"     # same gap again -> no duplicate issue
    d.store.st["gap_reported_for"] = "2026-11-24 09:00:00"
    r.iteration()
    assert len(d.issues.made) == n


def test_dry_run_sends_to_test_address_and_marks_nothing():
    rows = [row("a@x", send_at="2026-11-30 09:30"), row("b@x"), row("c@x")]
    r, d = make(rows, at("02:00"), sending=False, dry="me@iitb.ac.in")
    r.run(run_seconds=30 * 60)
    assert [to for to, _, _ in d.mailer.sent] == ["me@iitb.ac.in", "me@iitb.ac.in"]
    times = [t for _, _, t in d.mailer.sent]
    assert (times[1] - times[0]).total_seconds() >= 60
    assert all(x["status"] == "approved" for x in d.store.rows)
    assert d.git.pushes == 0 and d.issues.made == [] and d.chained == 0


def test_self_chain_near_end_while_work_remains():
    rows = [row(f"p{i}@x", send_at="2026-11-25 09:30") for i in range(3)]
    r, d = make(rows, at("09:00"))
    r.run(run_seconds=20 * 60)
    assert d.chained == 1


def test_no_chain_when_nothing_scheduled_and_old_sends():
    st = S.default_state()
    st["last_real_send_at"] = "2026-09-01 09:30:00"
    r, d = make([row("a@x", status="sent", sent_at="2026-09-01 09:30:00")], at("09:00"), st=st)
    r.run(run_seconds=20 * 60)
    assert d.chained == 0 and d.git.pushes == 1          # one check, then exit


# ------------------------------------------------------------------ conflict reconcile
def test_reconcile_keeps_runner_sends_and_laptop_queue():
    runner = [row("a@x", status="sent", sent_at="2026-11-24 09:30:00", message_id="<1>"),
              row("b@x"),
              row("gone@x", status="sent", sent_at="2026-11-24 09:31:00", message_id="<2>")]
    laptop = [row("a@x"),                                   # laptop still thinks approved
              row("b@x", opening_line="Edited line."),      # laptop edited an unsent row
              row("new@x", send_at="2026-11-25 09:30")]     # laptop queued a new one
    out = {r["email"]: r for r in S.reconcile(runner, laptop)}
    assert out["a@x"]["status"] == "sent" and out["a@x"]["message_id"] == "<1>"
    assert out["b@x"]["opening_line"] == "Edited line." and out["b@x"]["status"] == "approved"
    assert out["new@x"]["status"] == "approved"
    assert out["gone@x"]["status"] == "sent"                # a sent record is never lost


def test_reconcile_keeps_laptop_replied_mark():
    runner = [row("a@x", status="sent", sent_at="2026-11-24 09:30:00", message_id="<1>")]
    laptop = [row("a@x", status="replied")]
    assert S.reconcile(runner, laptop)[0]["status"] == "replied"
    assert S.reconcile(runner, laptop)[0]["message_id"] == "<1>"


# ------------------------------------------------------------------ reconcile with real git (rejected push)
def test_rejected_push_is_rebuilt_on_origin(tmp_path, monkeypatch):
    import subprocess
    import send

    def git(cwd, *a):
        subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)

    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    git(tmp_path, "clone", "-q", str(origin), str(seed))
    for c in (seed,):
        git(c, "config", "user.email", "t@t"); git(c, "config", "user.name", "t")
    (seed / "data").mkdir()
    S.save_rows(seed / "data/batch.csv", [row("a@x"), row("b@x")], send.FIELDS)
    S.save_state(seed / "data/runner_state.json", S.default_state())
    git(seed, "add", "-A"); git(seed, "commit", "-qm", "seed"); git(seed, "push", "-q", "origin", "main")

    laptop, runner = tmp_path / "laptop", tmp_path / "runner"
    for c in (laptop, runner):
        git(tmp_path, "clone", "-q", str(origin), str(c))
        git(c, "config", "user.email", "t@t"); git(c, "config", "user.name", "t")

    # laptop queues a new professor and pushes first
    rows = S.load_rows(laptop / "data/batch.csv") + [row("new@x", send_at="2026-11-25 09:30")]
    S.save_rows(laptop / "data/batch.csv", rows, send.FIELDS)
    git(laptop, "commit", "-qam", "queue new"); git(laptop, "push", "-q", "origin", "main")

    # runner sent a@x (without having pulled) -> its push is rejected -> reconcile
    monkeypatch.chdir(runner)
    rrows = S.load_rows("data/batch.csv")
    rrows[0].update(status="sent", sent_at="2026-11-24 09:30:00", message_id="<1>")
    S.save_rows("data/batch.csv", rrows, send.FIELDS)
    st = S.default_state(); st["last_sent_at"] = "2026-11-24 09:30:00"
    S.save_state("data/runner_state.json", st)

    g = A.Git(["data/batch.csv", "data/runner_state.json"])
    store = T.Store.__new__(T.Store)
    read = lambda: (S.load_rows("data/batch.csv"), S.load_state("data/runner_state.json"))
    def write(rows, st):
        S.save_rows("data/batch.csv", rows, send.FIELDS); S.save_state("data/runner_state.json", st)
    ok = g.commit_push("runner", read, write, lambda mine: S.reconcile(mine, S.load_rows("data/batch.csv")))
    assert ok

    check = tmp_path / "check"
    git(tmp_path, "clone", "-q", str(origin), str(check))
    final = {r["email"]: r for r in S.load_rows(check / "data/batch.csv")}
    assert final["a@x"]["status"] == "sent" and final["a@x"]["message_id"] == "<1>"   # runner's send kept
    assert final["new@x"]["status"] == "approved"                                       # laptop's queue kept
    assert S.load_state(check / "data/runner_state.json")["last_sent_at"] == "2026-11-24 09:30:00"


# ------------------------------------------------------------------ daily queueing
def test_queue_today_rules():
    sys.path.insert(0, str(ROOT / "scripts"))
    import queue_today as Q
    hol = {"2026-11-24"}
    assert "holiday" in Q.skip_reason(at("00:00", "2026-11-24"), hol)
    assert "Saturday" in Q.skip_reason(at("00:00", "2026-11-28"), hol)
    assert Q.skip_reason(at("00:00", "2026-11-25"), hol) == ""
    rows = [row(f"p{i}@x", send_at="") for i in range(100)] + [row("old@x", status="sent", send_at="")]
    chosen, already = Q.pick(rows, "2026-11-25")
    assert len(chosen) == 90 and already == 0 and all(r["status"] == "approved" for r in chosen)
    rows[0]["send_at"] = "2026-11-25 08:30"            # 1 already queued today -> 89 more at most
    chosen, already = Q.pick(rows, "2026-11-25")
    assert already == 1 and len(chosen) == 89
    assert Q.holidays(ROOT / "data" / "holidays.txt") >= {"2026-11-24", "2026-12-25"}
