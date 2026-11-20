# STATE.md — handoff file (read this first in a new session)

The full original brief, with all working rules, is in the first message of the original chat. Key rules: ask and never assume; plain language; no outward-facing action without the user's explicit "yes" each time; never invent or construct email addresses; professor data comes only from plain Python scripts that read official pages (no AI lookups or subagents); credentials never go in chat or files.

## Current phase
**Phase 0: Discovery (questions only, nothing built yet).**

## Done
- 2026-11-05: Created the project folder. Recorded the batch 1 answers (goal, areas, timing, institutes, target count, coursework) in DECISIONS.md.

- 2026-11-05: Batch 2 answered. Resume saved at resume.pdf and read. Fields, institute order (ABC + Lucknow first) and "show CPI" recorded. Wrote 2 sample emails in email_samples.md.

- 2026-11-06: User supplied a model email to follow. Wrote adapted draft v1 in email_template_draft.md (waiting for phone, email, approval).

- 2026-11-06: User asked for a shorter email like a second example. Replaced the draft with a short v2 (email_template_draft.md). Still waiting for phone, email, approval.

- 2026-11-06: User gave phone (8169991371) and signature email (25B2704@iitb.ac.in). Filled into draft v2.

- 2026-11-06: User uploaded a professor database (xlsx). Inspected it read-only; summary in DECISIONS.md (batch 4). Waiting for scope/department/method answers.

- 2026-11-06: User chose all 6 IIMs (A, B, C, L, K, Mumbai), no department filter, 150 professors, ~3 projects per email. Looked at the other resumes in the parent folder (other students' resumes, no research internships under professors).

- 2026-11-06: Sending account = IITB email. 25 per IIM approved. Wrote draft v3 with 5 field variants for the user to review.

- 2026-11-06: Draft v4 written. User chose high volume (~150), slots 08:00 and 13:00 IST, 1 minute apart, follow-ups wanted. Checked tools: git and Python ok, GitHub CLI missing.

- 2026-11-06: Draft v5 written. Read IITB webmail login page for server settings (recorded in DECISIONS.md batch 8).

- 2026-11-06: Draft v5 wording fixed. GitHub CLI installed on this PC. Password plan = GitHub Secret, private repo.

- 2026-11-06: User shared a senior's prompt and a sample email as the style to follow. Raised doubts (see DECISIONS.md batch 10). Waiting for answers before rewriting the draft.

- 2026-11-06: Style questions answered. Wrote email_template_v6.md. Round 1 = IIM A, B, C, Lucknow; slow ramp-up.

- 2026-11-06: Phase 1 started. Wrote scripts/common.py (polite cached fetch) and probe/inspect scripts. IIMA, IIMC, IIML directories readable; IIMB gives 403.

- 2026-11-19: GitHub CLI logged in as `arnavjain16` (browser code flow done by the user; scopes repo, workflow, read:org, gist). No repo created, nothing pushed.

- 2026-11-19: User: target only the IIMs for now; startups get their own repo later (user will say when). GitHub repo `startup-mailer` renamed to **https://github.com/arnavjain16/iims-mailer** (private). This folder (`cold-mailer/`) is now its git repo; startup files removed from it (`startups/` folder is git-ignored, unlinked from any remote, history kept locally). Repo already has secret `IITB_PASSWORD` (added by the user) and variables `IITB_USERNAME=25B2704`, `SENDING_ENABLED=false`. Sending from 25b2704@iitb.ac.in only. No workflow in the repo yet, so nothing can send. The professor xlsx is git-ignored (not a data source).

- 2026-11-19: IIM Mumbai scraped (user said yes): 51 professors, 51 official @iimmumbai.ac.in emails, 41 with research areas -> data/iim_mumbai.csv. Appended to the xlsx sheet 'IIMs  ISB' rows 374-424 with new columns Research Areas / Source Page / Designation / Added (backup in data/). IIM Bangalore: 3 Haiku agents all got 403, 0 rows.

- 2026-11-19: IIM Bangalore read in the user's Chrome: 109 professors, 108 official emails. xlsx now: IIM B 124 rows (35 confirmed, 2 + 15 flagged CHECK, 72 new). Details in DECISIONS.md.

- 2026-11-20: IIM A/C/L verified against official sites and senior's list merged (DECISIONS.md). Database: 455 IIM rows, 337 verified, 55 flagged CHECK, 63 unverified (all IIM K).

## Next
- (newest) Choose the 150 (25 per IIM) from the database; answer '15 emails' (total vs per IIM); then build the IIM sender + workflow.
- (newest, 2026-11-19) Build the IIM sender + scheduled workflow in this repo (adapt `startups/scripts/send.py`, IITB SMTP) after the scraper output is approved.
- (newest, Phase 1) User confirms directory links, decides what to do about IIM Bangalore, and says whether "15 emails" is the total or per IIM. Then: write the scraper, show output for 10 professors from one IIM, wait for approval.
- (newest) User: switch on GitHub two-step login; give follow-up timing; approve moving from Phase 0 to Phase 1 (IIM faculty page scripts). Phase 1 starts by confirming the official directory links with the user.
- (newest) Answers on: how personalised the lines may be (rule 8), which resumes, which PDF to attach, email length, summaries per professor.
- (newest) Need: approve v5; GitHub 2-step login on? ; ramp-up answer; then Phase 1.
- (newest) Need: approve v5; decide how to store the IITB password (GitHub Secret vs run from laptop); follow-up days; repo type; yes to install GitHub CLI; ramp-up answer.
- (newest) Need: webmail address, follow-up timing, repo type, yes to install GitHub CLI later, confirm volume plan and draft v4. Then Phase 1.
- (newest) User reviews draft v3. Then: IITB mail login method, remote/on-campus, DOB/gender, daily volume, follow-ups, GitHub account, private vs public repo.
- (newest) Answers needed: how to pick 150 of ~290; the second quant/time-series project; sending account and daily volume; remote/on-campus; approve short draft; DOB/gender on resume.
- (new) Answers on the database: scope, departments to keep, domain-matching method, target total, blank institute = Lucknow?
- Get the remaining batch 3 answers: approve draft v2; confirm the sending account; remote/on-campus; round 1 split; DOB/gender on resume.
- Then the sending account and app password, daily volume, time window, follow-ups, GitHub account, private vs public repo.
- Then batch 4: sending account and app password, daily volume, time window, follow-ups.
- Then batch 5: GitHub account, private vs public repo.

## Timing note
The internship starts in December 2026 and today is 2026-11-05, so the schedule is tight. Emails should ideally go out in mid-November.

## Files
- `DECISIONS.md`: the user's answers.
- `STATE.md`: this file.
