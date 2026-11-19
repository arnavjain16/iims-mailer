# DECISIONS.md: startup cold mailer (the user's answers)

Answers are recorded as given. Open items are marked **PENDING**.

## 2026-11-11: brief
- **Goal:** cold-email startups for internships in roles that match the resume: founder's office, strategy, finance, business ops / product, and VC investment analyst. "As many as possible", Mumbai preferred.
- **Method:** same process as the professor cold mailer (`../STATE.md`, `../DECISIONS.md`): a database, approval before sending, a private GitHub repo, the password kept as a GitHub Secret, scheduled sending so the laptop can be off.
- ~~Sending account: personal Gmail~~ (replaced on 2026-11-19, see below).

## 2026-11-19: sending account changed to IITB
- **Sending account:** **25b2704@iitb.ac.in** only. Gmail is NOT used. SMTP `smtp-auth.iitb.ac.in` port 587 (STARTTLS), normal IITB (LDAP) login. IITB has no app passwords, so the real IITB password is stored only as the GitHub Secret `IITB_PASSWORD` on the private repo, typed by the user on GitHub's website, never in chat or files. The login name is the plain repo variable `IITB_USERNAME`.
- **Signature email:** 25B2704@iitb.ac.in, so replies come to the sending inbox. Phone +91 8169991371.
- **Your copy:** every first email is BCC'd to 25b2704@iitb.ac.in (the server keeps no Sent copy for a script).
- **Replies:** the Gmail reply checker was removed. Replies are not read automatically; mark them with `manage.py replied`. Follow-ups are OFF until the repo variable `FOLLOWUPS_ENABLED` is `true`.

## Carried over from the professor mailer (same rules)
- Email addresses come only from the organisation's own website. Never guessed or constructed. Each address records the page it was found on.
- No outward action without the user's explicit yes. Slow ramp-up: start small, then increase.
- Send slots: 08:00 and 13:00 IST, Monday to Friday, about 1 minute apart (60–75 s).
- One follow-up after 5 working days with no reply, in the same thread.
- One resume (`resume.pdf`), attached to every email. Every fact about Arnav comes from it.

## Assumptions to confirm (PENDING)
- Availability line: "winter internship from December 2026 to January 2027, on-site in Mumbai or remotely, and can continue part-time after that."
- First scheduled slot size: 5 per slot (repo variable `SLOT_LIMIT`), raised after the first replies and bounces are checked.
- VC partners' personal emails printed on fund websites (India Quotient, Waterbridge, Stellaris, DSG) are NOT used unless the user says so.
