"""
Sends the IIM professor emails from Arnav's IIT Bombay mailbox (25b2704@iitb.ac.in). Never Gmail.

The list is data/batch.csv (open it in Excel to review). One row per professor:
  name, surname, institute, email, field (A-E: which project paragraph), subject_topic,
  opening_line, profile_url, status, sent_at, message_id
status: draft -> approved (by the user) -> sent.  Only 'approved' rows are emailed, each once.

Safety:
  * IITB password from the IITB_PASSWORD env var (a GitHub Secret) or a hidden prompt; never stored.
    Login name from IITB_USERNAME.
  * --dry-run prints the emails and sends nothing. --test-to sends ONE sample to that address only.
  * Every real email is BCC'd to 25b2704@iitb.ac.in so the inbox shows exactly what went out.
  * Stops at a login error (no retries, so the account is not locked) or after 2 send errors in a row.
  * ~60-75 s between emails.

  python scripts/send.py --dry-run --limit 3
  python scripts/send.py --test-to 25b2704@iitb.ac.in
  python scripts/send.py --limit 10
"""
import argparse
import csv
import getpass
import os
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / "data" / "batch.csv"
RESUME = ROOT / "resume.pdf"
SMTP_HOST, SMTP_PORT = "smtp-auth.iitb.ac.in", 587
FROM_NAME, FROM_ADDR = "Arnav Jain", "25b2704@iitb.ac.in"
IST = timezone(timedelta(hours=5, minutes=30))
FIELDS = ["name", "surname", "institute", "email", "field", "subject_topic", "opening_line",
          "profile_url", "status", "sent_at", "message_id"]

# Project paragraphs, by field (email_template_v6.md). Every fact comes from resume.pdf.
PROJECTS = {
    "A": "I have reviewed 20+ peer-reviewed papers on greenwashing in sustainable finance, researched UPI's business model and India's CBDC (top 10 of 300+ teams), and built a CAPM-WACC DCF valuation in an equity research report that reached the final top 10 of the Finance Club's competition at IIT Bombay.",
    "B": "I have researched UPI's business model and the rise of India's CBDC (top 10 of 300+ teams), reviewed 20+ peer-reviewed papers on greenwashing in sustainable finance, and traced a company's fall in ROCE through a DuPont analysis in an equity research report.",
    "C": "I have developed a data-driven framework to estimate venue investment returns (IRR) for a strategic consulting project with PlayAll Sports, researched UPI intermediaries' revenue models (top 10 of 300+ teams), and written an equity research report that reached the final top 10 at IIT Bombay.",
    "D": "I have worked on financial and quantitative modelling projects, including portfolio allocation using regime-switching models, DCF valuation, and a venue investment IRR framework.",
    "E": "I have designed a data schema covering pricing, demographics, competition and utilisation for a venue investment project with PlayAll Sports, researched UPI's business model (top 10 of 300+ teams), and written an equity research report on SPR Auto Technologies that reached the final top 10 at IIT Bombay.",
}

BODY = """Dear Professor {surname},

I am an undergraduate at IIT Bombay, currently pursuing a Minor in AI & Data Science, and I am writing to express my interest in your research. {opening_line}

{projects}

I am very eager to learn and willing to pick up any new skills your projects need. I would be grateful for the opportunity to contribute to your research in any role you find useful, under your guidance.

My resume is attached for your review. Thank you for your time and consideration.

Sincerely,
Arnav Jain

--
Arnav Jain
B.S., Centre for Multidisciplinary Education, Minor in Artificial Intelligence and Data Science
Indian Institute of Technology Bombay
25b2704@iitb.ac.in
"""


def render(row):
    for k in ("surname", "opening_line", "subject_topic"):
        if not row.get(k, "").strip():
            raise ValueError(f"{row['name']}: '{k}' is empty")
    if row["field"] not in PROJECTS:
        raise ValueError(f"{row['name']}: field must be one of A-E")
    subject = f"Interest in Research on {row['subject_topic'].strip()}"
    body = BODY.format(surname=row["surname"].strip(), opening_line=row["opening_line"].strip(),
                       projects=PROJECTS[row["field"]])
    return subject, body


def build(to, subject, body, bcc=None):
    m = EmailMessage()
    m["From"] = f"{FROM_NAME} <{FROM_ADDR}>"
    m["To"] = to
    m["Subject"] = subject
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain="iitb.ac.in")
    if bcc:
        m["Bcc"] = bcc
    m.set_content(body)
    m.add_attachment(RESUME.read_bytes(), maintype="application", subtype="pdf",
                     filename="Arnav_Jain_Resume_IITB.pdf")
    return m


def connect(user, password):
    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60)
    s.ehlo()
    s.starttls(context=ssl.create_default_context())
    s.ehlo()
    s.login(user, password)
    return s


def load():
    with BATCH.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    tmp = BATCH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(BATCH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--gap", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test-to", default="")
    args = ap.parse_args()

    if not RESUME.exists():
        sys.exit(f"Resume not found at {RESUME}")
    rows = load()
    if args.test_to:
        pool = [r for r in rows if r["status"] in ("approved", "draft")][:1]
    else:
        pool = [r for r in rows if r["status"] == "approved"][:args.limit]
    if not pool:
        print("Nothing to send.")
        return
    plan = []
    for r in pool:
        subject, body = render(r)                      # fails loudly on an incomplete row
        plan.append((r, args.test_to or r["email"], subject, body))

    print(f"{len(plan)} {'TEST' if args.test_to else 'real'} email(s){' (DRY RUN)' if args.dry_run else ''}:")
    for r, to, s, _ in plan:
        print(f" - {r['name']:<32} {r['institute']:<10} -> {to}   [{s}]")
    if args.dry_run:
        print("\n----- first email -----\nTo: %s\nSubject: %s\n\n%s" % (plan[0][1], plan[0][2], plan[0][3]))
        return

    user = os.environ.get("IITB_USERNAME") or input("IITB login name: ").strip()
    password = os.environ.get("IITB_PASSWORD") or getpass.getpass("IITB password (hidden): ")
    try:
        smtp = connect(user, password)
    except smtplib.SMTPAuthenticationError as exc:
        sys.exit(f"IITB login failed, nothing sent (not retrying, to avoid locking the account): {exc}")

    fails = 0
    for i, (r, to, subject, body) in enumerate(plan):
        msg = build(to, subject, body, bcc=None if args.test_to else FROM_ADDR)
        try:
            try:
                smtp.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                smtp = connect(user, password)
                smtp.send_message(msg)
        except Exception as exc:
            fails += 1
            print(f"FAILED {r['name']}: {exc}")
            if fails >= 2:
                sys.exit("Two failures in a row; stopping.")
            continue
        fails = 0
        stamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
        print(f"[{i + 1}/{len(plan)}] sent {r['name']} -> {to}  {stamp} IST")
        if not args.test_to:
            r.update(status="sent", sent_at=stamp, message_id=msg["Message-ID"])
            save(rows)                                  # saved after EVERY email
        if i < len(plan) - 1:
            time.sleep(args.gap + random.randint(0, 15))
    smtp.quit()
    print("Done.")


if __name__ == "__main__":
    main()
