"""
Everything the runner does to the outside world, kept small so tests can replace it with fakes.

  Mailer  - SMTP (reuses send.render / send.build / send.connect)
  Replies - IMAP, read-only (never marks or moves messages)
  Issues  - GitHub Issues via the gh CLI
  Git     - pull / commit / push with record-level reconcile on a rejected push

Errors are logged by TYPE or numeric SMTP CODE only. Credentials are never printed.
"""
import email
import imaplib
import re
import smtplib
import ssl
import subprocess
from email.header import decode_header, make_header
from email.utils import parseaddr

import send  # scripts/send.py (on sys.path)


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- SMTP
class AuthFailed(Exception):
    pass


class Rejected(Exception):
    def __init__(self, code):
        super().__init__(f"SMTP {code}")
        self.code = code


class Transient(Exception):
    pass


class Mailer:
    def __init__(self, user, token):
        self.user, self.token, self.smtp = user, token, None

    def _conn(self):
        if self.smtp is None:
            try:
                self.smtp = send.connect(self.user, self.token)
            except smtplib.SMTPAuthenticationError as e:
                raise AuthFailed(f"SMTP {e.smtp_code}") from None
            except (OSError, smtplib.SMTPException) as e:
                raise Transient(type(e).__name__) from None
        return self.smtp

    def send(self, row, to, bcc):
        """Send one email; returns its Message-ID. Raises AuthFailed / Rejected / Transient."""
        subject, body = send.render(row)
        msg = send.build(to, subject, body, bcc=bcc)
        for attempt in (1, 2):                       # one reconnect if the server dropped us
            try:
                self._conn().send_message(msg)
                return msg["Message-ID"]
            except smtplib.SMTPServerDisconnected:
                self.smtp = None
                if attempt == 2:
                    raise Transient("SMTPServerDisconnected") from None
            except smtplib.SMTPAuthenticationError as e:
                raise AuthFailed(f"SMTP {e.smtp_code}") from None
            except smtplib.SMTPRecipientsRefused as e:
                codes = [c for c, _ in e.recipients.values()]
                raise Rejected(codes[0] if codes else 550) from None
            except smtplib.SMTPResponseException as e:   # sender refused, data error, ...
                raise Rejected(e.smtp_code) from None
            except (OSError, smtplib.SMTPException) as e:
                self.smtp = None
                raise Transient(type(e).__name__) from None

    def close(self):
        if self.smtp is not None:
            try:
                self.smtp.quit()
            except Exception:
                pass
            self.smtp = None


# ---------------------------------------------------------------- IMAP replies
def _h(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def _excerpt(msg, limit=200):
    text = ""
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if part.get_content_type() == "text/plain" and not part.get_filename():
            try:
                text = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
            except Exception:
                text = ""
            break
    lines = []
    for line in text.splitlines():
        if line.startswith(">") or re.match(r"^On .+wrote:\s*$", line.strip()):
            break
        if line.strip():
            lines.append(line.strip())
    return " ".join(lines)[:limit]


class Replies:
    """Read-only IMAP: finds messages that answer one of our sent emails."""

    def __init__(self, user, token, own_address):
        self.user, self.token, self.own = user, token, own_address.lower()
        self.imap = None

    def _conn(self):
        if self.imap is None:
            ctx = ssl.create_default_context()
            ctx.set_ciphers("DEFAULT:AES256-GCM-SHA384")   # the TLS 1.2 cipher IITB offers; checks stay ON
            self.imap = imaplib.IMAP4_SSL("imap.iitb.ac.in", 993, ssl_context=ctx, timeout=30)
            self.imap.login(self.user, self.token)
        self.imap.select("INBOX", readonly=True)
        return self.imap

    def poll(self, rows, st):
        """Return (uidvalidity, [reply dicts]) for NEW messages matching a sent row. Never modifies the mailbox."""
        sent = [r for r in rows if (r.get("message_id") or "").strip()]
        if not sent:
            return st.get("uidvalidity", ""), []
        by_mid = {r["message_id"].strip(): r for r in sent}
        by_addr = {r["email"].strip().lower(): r for r in sent}
        try:
            m = self._conn()
        except Exception:
            self.imap = None
            raise
        uv = m.untagged_responses.get("UIDVALIDITY", [b""])[0]
        uv = uv.decode() if isinstance(uv, bytes) else str(uv)
        seen = set(st.get("seen_uids", [])) if st.get("uidvalidity") == uv else set()
        first = min(r["sent_at"][:10] for r in sent if r.get("sent_at"))
        since = __import__("datetime").datetime.strptime(first, "%Y-%m-%d").strftime("%d-%b-%Y")
        typ, data = m.uid("SEARCH", None, "SINCE", since)
        uids = [int(u) for u in (data[0] or b"").split()] if typ == "OK" else []
        found = []
        for uid in uids:
            if uid in seen:
                continue
            typ, d = m.uid("FETCH", str(uid), "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT IN-REPLY-TO REFERENCES)])")
            if typ != "OK" or not d or not isinstance(d[0], tuple):
                continue
            hdr = email.message_from_bytes(d[0][1])
            frm = parseaddr(hdr.get("From", ""))[1].lower()
            refs = (hdr.get("In-Reply-To", "") + " " + hdr.get("References", "")).split()
            row = next((by_mid[x] for x in refs if x in by_mid), None) or (by_addr.get(frm) if frm != self.own else None)
            if row is None or frm == self.own:
                found.append({"uid": uid, "row": None})          # not a reply to us: just remember it
                continue
            typ, d = m.uid("FETCH", str(uid), "(BODY.PEEK[]<0.200000>)")
            excerpt = _excerpt(email.message_from_bytes(d[0][1])) if typ == "OK" and d and isinstance(d[0], tuple) else ""
            found.append({"uid": uid, "row": row, "from": frm, "subject": _h(hdr.get("Subject", "")),
                          "excerpt": excerpt})
        return uv, found

    def close(self):
        if self.imap is not None:
            try:
                self.imap.logout()
            except Exception:
                pass
            self.imap = None


# ---------------------------------------------------------------- GitHub Issues
class Issues:
    def __init__(self, repo):
        self.repo = repo
        for name, color in (("reply", "0e8a16"), ("needs-attention", "d93f0b")):
            self._gh(["label", "create", name, "--color", color, "--force"])

    def _gh(self, args):
        r = subprocess.run(["gh", *args, "-R", self.repo], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(f"gh exit {r.returncode}")
        return r.stdout

    def create(self, title, body, label):
        """True if the Issue was created; errors are logged and skipped."""
        try:
            self._gh(["issue", "create", "--title", title[:200], "--body", body, "--label", label])
            return True
        except Exception as e:
            log(f"issue error: {type(e).__name__}")
            return False


# ---------------------------------------------------------------- git
class Git:
    def __init__(self, files):
        self.files = files      # paths (relative to repo root) the runner commits

    def _run(self, *args, check=True):
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=120)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {args[0]} exit {r.returncode}")
        return r

    def pull(self):
        """Bring in laptop changes. If our last push failed (we are ahead), leave it to push()."""
        self._run("fetch", "-q", "origin", "main")
        ahead = int(self._run("rev-list", "--count", "origin/main..HEAD").stdout.strip() or 0)
        if ahead == 0:
            self._run("merge", "-q", "--ff-only", "origin/main")

    def commit_push(self, message, read_mine, write_merged, reconcile_fn):
        self._run("add", *self.files)
        if self._run("diff", "--cached", "--quiet", check=False).returncode != 0:
            self._run("commit", "-q", "-m", message)
        for _ in range(3):
            if self._run("rev-list", "--count", "origin/main..HEAD").stdout.strip() == "0":
                return True
            if self._run("push", "-q", "origin", "HEAD:main", check=False).returncode == 0:
                return True
            # rejected: rebuild on origin/main, merging the laptop's queue with our send records
            mine_rows, mine_state = read_mine()
            self._run("fetch", "-q", "origin", "main")
            self._run("reset", "-q", "--hard", "origin/main")
            write_merged(reconcile_fn(mine_rows), mine_state)
            self._run("add", *self.files)
            if self._run("diff", "--cached", "--quiet", check=False).returncode != 0:
                self._run("commit", "-q", "-m", message + " (reconciled)")
        return False
