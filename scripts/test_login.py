"""
Checks ONLY whether the IITB mail server accepts your login. Sends nothing.
Run it in a normal Windows PowerShell window (not the app's terminal panel).
The password is typed hidden and never saved. Makes exactly ONE login attempt.

  python scripts/test_login.py
"""
import base64
import getpass
import smtplib
import ssl

HOST, PORT = "smtp-auth.iitb.ac.in", 587

user = (input("IITB login name [25b2704]: ").strip() or "25b2704").lower()
password = getpass.getpass("IITB password (hidden, not saved): ")
print(f"Using login name: {user!r}")
print(f"Password length typed: {len(password)} characters; "
      f"starts/ends with a space: {password[:1] == ' ' or password[-1:] == ' '}; "
      f"only plain keyboard characters: {password.isascii()}")
try:
    s = smtplib.SMTP(HOST, PORT, timeout=30)
    s.ehlo()
    s.starttls(context=ssl.create_default_context())
    s.ehlo()
    # ONE attempt with AUTH PLAIN (smtplib.login would try PLAIN and then LOGIN = two failures)
    token = base64.b64encode(f"\0{user}\0{password}".encode("utf-8")).decode()
    code, resp = s.docmd("AUTH", "PLAIN " + token)
    if code == 235:
        print("LOGIN OK: the IITB server accepted this login name and password.")
    else:
        print("LOGIN REJECTED:", code, resp.decode(errors="replace"))
    s.quit()
except Exception as e:
    print("Could not connect:", type(e).__name__, e)
