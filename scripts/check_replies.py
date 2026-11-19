"""
Reads the Gmail inbox (read-only) and marks companies that replied or bounced,
so follow-ups never go to them. Runs on GitHub before every send.

  python scripts/check_replies.py      (password from GMAIL_APP_PASSWORD or a hidden prompt)
"""
import email
import getpass
import imaplib
import os
import sqlite3
import sys
from datetime import datetime
from email.utils import parseaddr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "startups.db"
USER = "arnavj3061@gmail.com"


def main():
    con = sqlite3.connect(DB_PATH)
    sent = con.execute("SELECT id, name, domain, chosen_email, sent_at FROM companies WHERE status='sent'").fetchall()
    if not sent:
        print("No sent emails yet; nothing to check.")
        return
    password = (os.environ.get("GMAIL_APP_PASSWORD") or getpass.getpass("Gmail app password (hidden): ")).replace(" ", "")
    first = min(datetime.strptime(s[4], "%Y-%m-%d %H:%M") for s in sent).strftime("%d-%b-%Y")
    senders, bounces = set(), []
    with imaplib.IMAP4_SSL("imap.gmail.com", 993) as im:
        im.login(USER, password)
        im.select("INBOX", readonly=True)
        _, data = im.search(None, f'(SINCE "{first}")')
        for num in data[0].split():
            _, hdr = im.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM)])")
            frm = parseaddr(email.message_from_bytes(hdr[0][1]).get("From", ""))[1].lower()
            if "mailer-daemon" in frm or "postmaster" in frm:
                _, full = im.fetch(num, "(BODY.PEEK[])")
                bounces.append(full[0][1].decode("utf-8", "replace").lower())
            else:
                senders.add(frm)
    replied = bounced = 0
    for cid, name, domain, addr, _ in sent:
        dom = domain.lower()
        alt = addr.split("@")[1].lower()
        if any(s.endswith("@" + d) or s.endswith("." + d) for s in senders for d in (dom, alt)):
            con.execute("UPDATE companies SET status='replied' WHERE id=?", (cid,))
            print(f"REPLY   {name}")
            replied += 1
        elif any(addr.lower() in b for b in bounces):
            con.execute("UPDATE companies SET status='bounced' WHERE id=?", (cid,))
            print(f"BOUNCED {name} ({addr})")
            bounced += 1
    con.commit()
    print(f"{replied} new replies, {bounced} new bounces.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
