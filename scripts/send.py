"""
Sends the startup internship emails from Arnav's IIT Bombay mailbox (25b2704@iitb.ac.in).

Safety:
  * Only companies whose status is 'approved' get an email (see manage.py).
  * A company is never emailed twice (its status becomes 'sent').
  * The IITB password comes from the IITB_PASSWORD environment variable
    (a GitHub Secret when run on GitHub), or from a hidden prompt on the laptop.
    It is never written to any file. The login name comes from IITB_USERNAME
    (a plain GitHub variable, not a secret).
  * --dry-run prints what would be sent and sends nothing.
  * Stops at a login error, or after 2 send errors in a row.
  * IITB mail does not keep a Sent copy for us, so every first email is also BCC'd to
    25b2704@iitb.ac.in: you see exactly what went out (and any bounce notices) in your inbox.
  * A failed login stops everything at once (repeated wrong logins could lock the account).

Examples (run from the repo folder):
  python scripts/send.py --test-to 25b2704@iitb.ac.in     one sample to yourself
  python scripts/send.py --dry-run --limit 5
  python scripts/send.py --limit 10                       next 10 approved, ~60 s apart
  python scripts/send.py --followups --days 5             follow-ups after 5 working days, no reply
"""
import argparse
import getpass
import os
import random
import smtplib
import sqlite3
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from template import FOLLOWUP, render  # noqa: E402

DB_PATH = ROOT / "startups.db"
RESUME = ROOT / "resume.pdf"
SMTP_HOST, SMTP_PORT = "smtp-auth.iitb.ac.in", 587      # STARTTLS, as listed on the IITB webmail login page
FROM_NAME, FROM_ADDR = "Arnav Jain", "25b2704@iitb.ac.in"
BCC_ADDR = FROM_ADDR                                      # your own copy of every real email
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M")


def working_days_since(stamp):
    start = datetime.strptime(stamp, "%Y-%m-%d %H:%M").date()
    today, d, n = datetime.now(IST).date(), start, 0
    while d < today:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def build(to, subject, body, in_reply_to=None, bcc=None):
    m = EmailMessage()
    m["From"] = f"{FROM_NAME} <{FROM_ADDR}>"
    m["To"] = to
    m["Subject"] = subject
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain="iitb.ac.in")
    if bcc:
        m["Bcc"] = bcc          # delivered to you, never shown to the company
    if in_reply_to:
        m["In-Reply-To"] = in_reply_to
        m["References"] = in_reply_to
    m.set_content(body)
    m.add_attachment(RESUME.read_bytes(), maintype="application", subtype="pdf",
                     filename="Arnav_Jain_Resume_IITB.pdf")
    return m


def connect(username, password):
    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60)
    s.ehlo()
    s.starttls(context=ssl.create_default_context())
    s.ehlo()
    s.login(username, password)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--gap", type=int, default=60, help="seconds between emails (plus 0-15 s random)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test-to", default="", help="send ONE sample email to this address only; changes nothing")
    ap.add_argument("--followups", action="store_true")
    ap.add_argument("--days", type=int, default=5, help="working days with no reply before the follow-up")
    args = ap.parse_args()

    if not RESUME.exists():
        sys.exit(f"Resume not found at {RESUME}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    if args.test_to:
        rows = con.execute("""SELECT * FROM companies WHERE chosen_email IS NOT NULL
                              ORDER BY (status='approved') DESC, (city='Mumbai') DESC, id LIMIT 1""").fetchall()
    elif args.followups:
        rows = [r for r in con.execute("""SELECT * FROM companies WHERE status='sent' AND followup_sent_at IS NULL
                                          ORDER BY sent_at""").fetchall()
                if working_days_since(r["sent_at"]) >= args.days][:args.limit]
    else:
        rows = con.execute("""SELECT * FROM companies WHERE status='approved' AND chosen_email IS NOT NULL
                              ORDER BY (city='Mumbai') DESC, id LIMIT ?""", (args.limit,)).fetchall()
    if not rows:
        print("Nothing to send.")
        return

    plan = []
    for r in rows:
        subject, body = render(r["name"], r["track"], r["what"], r["city"])
        if args.followups:
            role_short = "investment analyst " if r["track"] == "vc" else ""
            fu = FOLLOWUP.format(company=r["name"], role_short=role_short)
            quoted = "\n".join("> " + line for line in body.splitlines())
            body = f"{fu}\nOn {r['sent_at']} IST, Arnav Jain wrote:\n{quoted}\n"
            subject = "Re: " + subject
        plan.append((r, args.test_to or r["chosen_email"], subject, body))

    kind = "follow-up" if args.followups else ("TEST" if args.test_to else "first")
    print(f"{len(plan)} {kind} email(s){' (DRY RUN)' if args.dry_run else ''}:")
    for r, to, _, _ in plan:
        print(f" - {r['name']:<28} -> {to}")
    if args.dry_run:
        print("\n----- first email -----\nTo: %s\nSubject: %s\n\n%s" % (plan[0][1], plan[0][2], plan[0][3]))
        return

    username = os.environ.get("IITB_USERNAME") or input("IITB login name (the one you type in webmail): ").strip()
    password = os.environ.get("IITB_PASSWORD") or getpass.getpass("IITB password (hidden): ")
    try:
        smtp = connect(username, password)
    except smtplib.SMTPAuthenticationError as exc:
        sys.exit(f"IITB login failed, nothing sent (not retrying, to avoid locking the account): {exc}")

    fails = 0
    for i, (r, to, subject, body) in enumerate(plan):
        msg = build(to, subject, body, in_reply_to=r["message_id"] if args.followups else None,
                    bcc=None if args.test_to else BCC_ADDR)
        try:
            try:
                smtp.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                smtp = connect(username, password)
                smtp.send_message(msg)
        except Exception as exc:
            fails += 1
            print(f"FAILED {r['name']}: {exc}")
            if fails >= 2:
                sys.exit("Two failures in a row; stopping.")
            continue
        fails = 0
        stamp = now_ist()
        print(f"[{i + 1}/{len(plan)}] sent {r['name']} -> {to}  {stamp} IST")
        if not args.test_to:
            if args.followups:
                con.execute("UPDATE companies SET followup_sent_at=? WHERE id=?", (stamp, r["id"]))
            else:
                con.execute("UPDATE companies SET status='sent', sent_at=?, message_id=? WHERE id=?",
                            (stamp, msg["Message-ID"], r["id"]))
            con.commit()
        if i < len(plan) - 1:
            time.sleep(args.gap + random.randint(0, 15))
    smtp.quit()
    print("Done.")


if __name__ == "__main__":
    main()
