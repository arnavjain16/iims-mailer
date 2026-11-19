# DECISIONS.md: startup cold mailer (the user's answers)

Answers are recorded as given. Open items are marked **PENDING**.

## 2026-11-11: brief
- **Goal:** cold-email startups for internships in roles that match the resume: founder's office, strategy, finance, business ops / product, and VC investment analyst. "As many as possible", Mumbai preferred.
- **Method:** same process as the professor cold mailer (`../STATE.md`, `../DECISIONS.md`): a database, approval before sending, a private GitHub repo, the password kept as a GitHub Secret, scheduled sending so the laptop can be off.
- **Sending account:** personal Gmail **arnavj3061@gmail.com** (not the IITB account). Login uses a Gmail **App Password**, stored only as the GitHub Secret `GMAIL_APP_PASSWORD`. The user types it on GitHub's website, never in chat or files.
- **Signature email:** switched to arnavj3061@gmail.com so replies come to the sending inbox. Phone +91 8169991371.

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
