# Startup cold mailer (private)

Emails startups (Mumbai first) from **25b2704@iitb.ac.in** (IITB mail, never Gmail) about winter internships in founder's office, strategy, finance, product and VC analyst roles, with `resume.pdf` attached. GitHub Actions does the sending at **08:00 and 13:00 IST, Monday to Friday**, so the laptop can stay off.

Read first: `STATE.md` (where things stand) and `DECISIONS.md` (rules and answers).

## Files
- `seed_companies.csv`: companies to scan. Add rows to grow the list.
- `startups.db`: the database (companies, every email found with its source page, send status).
- `startups.xlsx`, `review.md`: readable views of the database. `sent_log.csv`: what was sent and when.
- `drafts_preview.md`: one sample email per track. `template.py`: the email text.
- `.github/workflows/send.yml`: the scheduled sender.

## Safety switches
- Only companies with status `approved` are emailed, and each one only once.
- Scheduled runs send ONLY when the repo variable `SENDING_ENABLED` is `true`. Set it to `false` to stop everything at once.
- `SLOT_LIMIT` (repo variable, default 5) caps each slot. `FOLLOWUP_DAYS` (default 5) is in working days.
- Replies are NOT read automatically. Mark them with `manage.py replied`. Follow-ups go out only when the repo variable `FOLLOWUPS_ENABLED` is `true`.
- Every first email is BCC'd to 25b2704@iitb.ac.in, so your inbox shows exactly what went out (and any bounces).
- The IITB password exists only as the GitHub Secret `IITB_PASSWORD`. A wrong password stops the run at once (no retries, so the account is not locked).

## One-time setup (you)
1. GitHub repo > Settings > Secrets and variables > Actions > **Secrets** > New repository secret: name `IITB_PASSWORD`, value = your IITB (LDAP) password.
2. Same page > **Variables** > New repository variable: name `IITB_USERNAME`, value = the login name you type in IITB webmail.
3. Enable the workflow: `gh workflow enable "Send startup emails"`.
4. GitHub repo > Actions > "Send startup emails" > **Run workflow**, mode `test`: one sample arrives in your IITB inbox.

## Day-to-day (on the laptop)
```
git pull                                       # always first: GitHub updates the database after each run
python scripts/manage.py skip --names "A,B"    # drop companies you don't want
python scripts/manage.py approve --ready       # approve everything with an address
python scripts/manage.py replied --name "X"    # if X replied somewhere the checker can't see
python scripts/manage.py export                # refresh xlsx / review.md
git add -A && git commit -m "approve batch" && git push
```
Grow the list: add rows to `seed_companies.csv`, run `python scripts/find_emails.py`, then `manage.py export`.
