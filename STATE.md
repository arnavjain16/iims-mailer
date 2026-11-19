# STATE.md: handoff file (read this first in a new session)

Rules are in DECISIONS.md. How-to is in README.md.

## Current phase
**Phase 3: set up sending (nothing sent yet).**

## Done
- 2026-11-11: Scanned 203 startups/VCs (seed_companies.csv). 95 have an address from their own site (76 in Mumbai); 108 must be applied to through their careers pages (review.md).
- 2026-11-11: Wrote the template (5 tracks), sender, reply checker and manage.py. Private GitHub repo with scheduled sending and a kill switch (`SENDING_ENABLED` repo variable).
- 2026-11-19: GitHub login done (account arnavjain16). Private repo created and pushed: https://github.com/arnavjain16/startup-mailer . Repo variable SENDING_ENABLED=false. Workflow disabled (paused).
- 2026-11-19: **Sending account changed to 25b2704@iitb.ac.in (IITB SMTP). Gmail is not used.** Secret `IITB_PASSWORD` + variable `IITB_USERNAME` replace `GMAIL_APP_PASSWORD`. Gmail reply checker removed; follow-ups gated by `FOLLOWUPS_ENABLED`. Pushed. Nothing sent.

## Next
1. User: add secret `IITB_PASSWORD` on GitHub's website. Set variable `IITB_USERNAME`.
2. Enable the workflow (`gh workflow enable "Send startup emails"`) and run it manually in mode `test`: one sample to 25b2704@iitb.ac.in. The user checks how it looks.
3. User approves the text and the list (`manage.py skip` / `approve --ready`), then pushes.
4. Set repo variable `SENDING_ENABLED=true` and `SLOT_LIMIT=5`. Watch the first day, then raise the limit.
