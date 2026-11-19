# Startup cold mailer (private)

Emails startups (Mumbai first) from **arnavj3061@gmail.com** about winter internships in founder's office, strategy, finance, product and VC analyst roles, with `resume.pdf` attached. GitHub Actions does the sending at **08:00 and 13:00 IST, Monday to Friday**, so the laptop can stay off.

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
- Before every run the inbox is checked. Companies that replied or bounced never get a follow-up.
- The Gmail App Password exists only as the GitHub Secret `GMAIL_APP_PASSWORD`.

## One-time setup (you)
1. Google Account > Security > turn on **2-Step Verification**.
2. Google Account > Security > **App passwords**: create one named "startup-mailer" and copy the 16 letters.
3. GitHub repo > Settings > Secrets and variables > Actions > **New repository secret**: name `GMAIL_APP_PASSWORD`, value = the 16 letters.
4. GitHub repo > Actions > "Send startup emails" > **Run workflow**, mode `test`: one sample arrives in your inbox.

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
