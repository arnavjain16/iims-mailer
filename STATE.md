# STATE.md: handoff file (read this first in a new session)

Rules are in DECISIONS.md. How-to is in README.md.

## Current phase
**Phase 3: set up sending (nothing sent yet).**

## Done
- 2026-11-11: Scanned 203 startups/VCs (seed_companies.csv). 95 have an address from their own site (76 in Mumbai); 108 must be applied to through their careers pages (review.md).
- 2026-11-11: Wrote the template (5 tracks), sender, reply checker and manage.py.
- 2026-11-11: The user chose Gmail arnavj3061@gmail.com plus a private GitHub repo with scheduled sending (same process as the professor mailer). Sender switched to Gmail SMTP; IITB code removed. GitHub Actions workflow added with a kill switch (`SENDING_ENABLED` repo variable).

## Next
1. User: GitHub CLI login (in progress), then create the private repo and push.
2. User: turn on Gmail 2-Step Verification, create an App Password, and add it as the repo secret `GMAIL_APP_PASSWORD` on GitHub's website.
3. Run the workflow manually in mode `test`: one sample to arnavj3061@gmail.com. The user checks how it looks.
4. User approves the text and the list (`manage.py skip` / `approve --ready`), then pushes.
5. Set repo variable `SENDING_ENABLED=true` and `SLOT_LIMIT=5`. Watch the first day, then raise the limit.
