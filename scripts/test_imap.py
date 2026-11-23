"""
Second check: does IITB's MAILBOX server (IMAP, the one mail apps read with) accept the same login?
Reads nothing, sends nothing. ONE login attempt. Run in a normal Windows PowerShell window.

  python scripts/test_imap.py
"""
import getpass
import imaplib
import ssl

user = (input("IITB login name [25b2704]: ").strip() or "25b2704").lower()
password = getpass.getpass("IITB password (hidden, not saved): ")
print(f"Using login name: {user!r}; password length {len(password)}")
def connect():
    try:
        return imaplib.IMAP4_SSL("imap.iitb.ac.in", 993, ssl_context=ssl.create_default_context(), timeout=30)
    except ssl.SSLError:
        # IITB's IMAP server only speaks older encryption settings; allow them for this connection only
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
        ctx.minimum_version = ssl.TLSVersion.TLSv1
        print("(using IITB's older encryption settings)")
        return imaplib.IMAP4_SSL("imap.iitb.ac.in", 993, ssl_context=ctx, timeout=30)


try:
    m = connect()
    m.login(user, password)
    print("IMAP LOGIN OK: the mailbox server accepts this login and password.")
    m.logout()
except imaplib.IMAP4.error as e:
    print("IMAP LOGIN REJECTED:", e)
except Exception as e:
    print("Could not connect:", type(e).__name__, e)
