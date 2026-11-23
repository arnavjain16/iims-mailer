# DECISIONS.md — the user's answers to Claude's questions

Answers are recorded as given. Nothing here is guessed; open items are marked **PENDING**.

## Phase 0, batch 1 (2026-11-05)

### What the user is looking for
- **Type:** Research internship.
- **Timing:** Winter break, starting **December 2026**, running **at least until end of January 2027**. Flexible to continue for further months.
- **Remote / on campus:** PENDING (asked in batch 2, not answered yet; asked again in batch 3).

### Subject areas
- **Primary:** Finance, Economics, Strategy.
- **Also open to:** "any fields related to the same" (exact adjacent areas PENDING, asked in batch 2).

### Institutes
- IIM Ahmedabad, IIM Bangalore, IIM Calcutta ("IIM ABC"), IIM Lucknow, IIM Mumbai, IIM Kozhikode. That is 6 institutes.
- **Total professors:** start with roughly **80**.
- **Professors / departments to avoid:** none.
- **How to split the 80 across institutes:** PENDING (batch 2).

### Project folder
- `C:\Users\ARNAV JAIN\Desktop\courses\99_inbox\resume\resume_making\cold-mailer` (approved).

## Phase 0, batch 2 (2026-11-05)

### Resume
- Saved at `cold-mailer/resume.pdf`. This is the file that gets attached, and the only source of facts about the user in emails.
- Facts printed on it: Arnav Jain; B.S., Centre for Multidisciplinary Education, IIT Bombay; graduating 2029; **CPI 9.13**; Minor in AI & Data Science (C-MInDS); SPI 9.42 in 2nd semester, ranked 3rd of 35+. Projects: greenwashing seminar (Prof. Ved Beloskar), FinSearch UPI/CBDC (top 10 of 300+ teams), equity research competition (top 10, SPR Auto DCF), PlayAll Sports venue IRR consulting project, WiDS financial modelling (Varun Beverages DCF), Summer of Quant. Associate Consultant, Consulting Core Group, UAC.
- The resume also shows date of birth and gender. Flagged to the user (their choice whether to keep these).

### Fields (final for now)
- **Include:** Finance, Economics, Strategy, Public Policy / Economics & Public Policy, Decision Sciences / Business Analytics / Operations Research.
- **Exclude:** Accounting, Entrepreneurship / Innovation.

### Institute order
- **Round 1:** IIM Ahmedabad, IIM Bangalore, IIM Calcutta, IIM Lucknow.
- **Round 2 (later):** IIM Mumbai, IIM Kozhikode.
- How the ~80 professors map onto these rounds: PENDING (batch 3).

### Email content
- **Show grades in the email:** YES (CPI 9.13, as printed on the resume).

## Phase 0, batch 3 (2026-11-06, partly answered)

- **Email template:** the user pasted another student's email as the model to follow and asked for phone number and email at the bottom. Adapted draft v1 is in `email_template_draft.md` (NOT approved yet). This replaces the A/B samples in `email_samples.md`.
- **Email length:** the user wants it SHORT (second example). Short draft v2 is in `email_template_draft.md`.
- **Phone number (signature):** 8169991371, shown as "+91 8169991371" (the +91 is my formatting, to be confirmed).
- **Email (signature):** 25B2704@iitb.ac.in.
- **Sending account:** NOT yet confirmed. The user gave the IITB address in reply to a question that asked about both the signature and the sending account, so this still needs a clear answer.
- **Still PENDING from batch 3:** approval of short draft v2; remote / on-campus line; round 1 split (~80 professors); whether to keep DOB/gender on the resume PDF.

## Phase 0, batch 4 (2026-11-06): the user's existing professor database

- User uploaded `Profs Database __ Kartik Vuthoo.xlsx` (looks like another student's list) and asked to (1) check it, (2) add more professors in the same domain, (3) research each professor's domain and customise each draft with the user's projects that match it.
- Contents (checked by script, nothing changed in the file):
  - Sheet "IIMs  ISB": ~335 rows. IIM A 68, IIM B 52, IIM C 56, IIM K 64, ISB 45, and 50 rows with a blank Institute cell whose emails all end in iiml.ac.in (probably IIM Lucknow, NOT yet confirmed by the user).
  - 4 rows have no email; 1 email appears twice (ashish@iiml.ac.in); 2 ISB rows have two emails in one cell. No IIM Mumbai rows.
  - Other sheets: NUS 26, NYU Stern 17, NTU 54 (pasted as text, messy), Cambridge 26, Umich 20, UC Berkeley 155.
  - Only a department/domain label per professor, no research areas, no page links, no note on where each email came from.
- Conflict flagged to the user: rule 5 (emails only from the professor's own official page) and rule 8 (no AI web search for professors/fields). The workbook emails are unverified; research areas must come from plain Python scripts reading official pages.
- PENDING answers: scope (IIMs only vs ISB and foreign universities); which departments to keep; approval of the keyword-rule method for matching projects; target total number; confirm blank-institute rows = IIM Lucknow.

## Phase 0, batch 5 (2026-11-06): answers to the database questions

- **Institutes, round 1 (all in the first batch):** IIM Ahmedabad, Bangalore, Calcutta, Lucknow, Kozhikode, and Mumbai. (The message said "Cozy Kore"; read as Kozhikode.)
- **Blank-institute rows in the database = IIM Lucknow:** confirmed.
- **Departments:** the user said "right now just apply to everyone; we'll reject the ones we don't want during the process" and added Marketing. My reading: no department filtering now; to be confirmed.
- **Target size:** 150 professors (the database already has ~290 for the five IIMs, so the choice of which 150 is PENDING).
- **Projects in emails:** about 3 per email: those matching the professor's field first, topped up from the other resume projects. Keep it short.
- **Derivatives / time series:** the user wants a project other than Summer of Quant added. The resume has no second time-series or derivatives project. PENDING: which one to use.
- **Resumes in the folder:** these are other students' resumes (consulting, P&G, engineering, one "External Research" resume). None lists a research internship under a professor. Used only for style. No facts from them go into any email.

## Phase 0, batch 6 (2026-11-06)

- **Sending account:** IIT Bombay email, 25B2704@iitb.ac.in. How the user logs in and whether SMTP/an app password works: PENDING.
- **25 professors per IIM** (6 institutes, 150 total): approved.
- **The database is only a reference.** Professors may also be found elsewhere, but only by Python scripts reading official faculty pages (rule 8 stays).
- **Email check:** the user wants each email checked against the professor's own web page before use. Plan: script compares the database address with the one printed on the official page; mismatches and unconfirmed addresses go to the user. A script cannot prove a mailbox works; only the first real batch shows bounces.
- **User asked to see the draft emails first.** Draft v3 (5 field variants) shown in `email_template_draft.md`. Awaiting feedback.

## Phase 0, batch 7 (2026-11-06)

- **Email wording:** no "can assist with X" lines. Instead one line: willing to contribute in whatever way the professor finds useful, open to any role. Strava teardown removed. Draft v4 in `email_template_draft.md`.
- **Remote / on campus:** open to either; settled per professor's reply. (Email says "remotely or on campus".)
- **Resume:** keep date of birth and gender as they are.
- **Mail access:** IIT Bombay WEBMAIL. The user will send the webmail address. Whether IMAP/SMTP works and how to log in from a script: PENDING. The password is never typed in chat.
- **Volume (user's choice, against my advice of 20-25/day):** about 150 emails, as many as possible, with a 1-minute gap between emails. Send slots at 08:00 and 13:00 IST: about 90 in the morning slot and the rest in the afternoon slot. Working days only. The first real batch is still small (Phase 4) and the daily cap stays adjustable.
- **Follow-ups:** YES wanted. Days and wording PENDING.
- **GitHub:** user has an account. No private/public repo decision yet (I recommended private). The GitHub CLI (`gh`) is NOT installed on this PC; installing it needs the user's yes.
- **PC tools found:** git 2.52, Python 3.14.4 with requests, bs4 and openpyxl.

## Phase 0, batch 8 (2026-11-06)

- **Draft v5:** NO dates in the email or subject; NO remote/on-campus mention (settled after the professor replies); Quant sentence made generic ("financial and quantitative modelling projects, including portfolio allocation using regime-switching models, DCF valuation, and a venue investment IRR framework"). Closing line: "I would love to contribute in whatever way you find useful and am open to any role."
- **Volume:** the user says the 1-minute gap is what keeps the IIT mailbox from flagging the sends. Kept as the user's plan; the daily cap stays adjustable. Ramp-up question not answered.
- **Webmail:** https://webmail.iitb.ac.in/ (the user's link was the inbox URL; the login page is the same site). The login page lists: IMAP imap.iitb.ac.in port 993 (SSL); SMTP smtp-auth.iitb.ac.in port 587 (STARTTLS); login = normal LDAP password; no app password mentioned. To be confirmed in the Phase 3 dry run.
- **Open risk:** no app password exists, so the sender would need the real IITB password stored as a GitHub Secret. The user decides (see STATE.md).

## Phase 0, batch 9 (2026-11-06)

- **Draft v5 wording fix:** "contribute" appeared twice. Now: "I am especially interested in {research area}. {PROJECT SENTENCE} I would love to contribute to your research in any role you find useful." (the contribute line comes last).
- **Password:** the user wants emails to go out even when the laptop is off, so the IITB password will be stored as a GitHub Secret on a PRIVATE repo (typed by the user on GitHub's website, never in chat or files). All tests run on GitHub, so the password never sits on the laptop.
- **Follow-up text:** to be decided later (timing still open; recommended 7 days, one follow-up).
- **GitHub CLI:** the user said yes to installing. Installed with winget (GitHub.cli 2.103.3, official GitHub release, hash verified). Login not done yet.

## Phase 0, batch 10 (2026-11-06): senior's style

- The user shared a senior's prompt and a screenshot of a finished email (sent to a professor at IIM B) as the STYLE to follow. Ignore the senior's own facts. Structure of the screenshot email: subject "Interest in Research on {area}"; "Dear Professor {Surname},"; paragraph 1 (who I am, interest in their research, their area); paragraph 2 (my matching projects); one line of eagerness; one line willing to learn / grateful to contribute under their guidance; "My resume is attached for your review. Thank you for your time and consideration."; "Sincerely," and a signature block with degree, institute, email.
- The senior's prompt asks for deep personalisation (opening line must reference the professor's research or a specific paper; 120-180 words; research summary + alignment + email per professor; use all 3 of the user's resumes).
- CONFLICTS with the user's earlier rules (5 and 8: no invented claims about a professor; no AI lookups of professors). Questions asked in the chat (how personal, which "three resumes", which PDF to attach, length, summaries).
- The user said to ask all doubts now. Answers PENDING.
- Draft v5 is superseded once the style questions are answered.

## Phase 0, batch 11 (2026-11-06): answers to the style questions

- **Personalisation = Option A:** opening line written from the professor's own page text saved by the script; paper named only by printed title; no claims about findings.
- **Resumes:** the user has ONE resume (`resume.pdf`). Only it is used and attached to every email.
- **Length:** about 150 words, like the screenshot.
- **Tone:** no flattery or clichés.
- **Research summary + alignment note per professor:** yes, saved as readable files in `profiles/`.
- **New template:** `email_template_v6.md` (replaces v5).
- **Ramp-up:** SLOW. The user's reason: the list is not big, and a wrong mass mailing could cost them their chances.
- **Order:** round 1 = IIM Ahmedabad, Bangalore, Calcutta, Lucknow (25 each). Kozhikode and Mumbai come later (25 each). Total plan still 150.
- **Volume per day:** to be decided after the first small batch (Phase 4). Send slots stay 08:00 and 13:00 IST, 1 minute apart.
- **Still PENDING:** GitHub two-step login (user action), follow-up timing (recommended 7 days), approval to leave Phase 0.

## Phase 0 closed; Phase 1 started (2026-11-06)

- **GitHub two-step login:** done by the user.
- **First real batch:** "15 emails to IIM A, B, C and Lucknow". Unclear whether 15 in total or 15 per IIM. Asked in chat. Mumbai later.
- **Follow-up:** 5 working days after the first email (wording to be decided later).
- **Phase 1 findings (scripts in `scripts/`, cache in `cache/`):**
  - IIM Ahmedabad: directory https://www.iima.ac.in/faculty-research/faculty-directory (200 OK); profiles at /faculty-research/faculty-directory/<Name>, reachable from the academic-area pages.
  - IIM Calcutta: directory https://www.iimcal.ac.in/faculty/faculty-directory (200 OK); profiles at /users/<id>; "Research Interests" printed on the profile.
  - IIM Lucknow: directory https://www.iiml.ac.in/faculty-profile (200 OK); profiles at faculty-data?n=<code>; email printed as name[at]iiml[dot]ac[dot]in.
  - IIM Bangalore: the site answers plain scripts with 403 Forbidden. NOT worked around. Options put to the user.

### Coursework (from the user's transcript screenshots, shared for context only)
These are reference only. Which items appear in the email is still to be decided.

**2025-26 Autumn (graded):** BB 101 Biology (AB), CH 111 Chemistry (AA), CH 117 Chemistry Lab (AA), MA 105 Calculus (BC), MS 101 Makerspace (AB), GC 101 Gender in the workplace (PP), NOCS01 NCC/NSS/NSO (PP).

**2025-26 Spring (graded):** CH 110 Interpretative Spectroscopy (AA), CS 101 Computer Programming and Utilization (AB), ENT101 Introduction to Innovation & Entrepreneurship (AB), PH 110 Introduction to Classical and Quantum Physics (AB), PH 117 Physics Lab (AA), SOM101 Introduction to Management (AA), NOCS02 NCC/NSS/NSO (PP), TA 101 TASET (PP).

**Current semester (grades not yet allotted):** DS 203 Programming for Data Science (Minor), EC 101 Economics (Department elective), EE 325 Probability and Random Processes (Additional Learning), IE 207 Industrial Systems (STEM Elective), IE 209 Linear Optimization and Network Flows (Additional Learning), MG 403 Accounting and Finance (HASMED Elective), LE 301 Seminar (Core), ES 250 / HS 250 Environmental Studies (Core).

## 2026-11-19: IIM Mumbai scraper, IIM Bangalore via AI agents
- **IIM Mumbai:** `scripts/scrape_iim_mumbai.py` reads https://iimmumbai.ac.in/faculty (6 pages, 51 professors) and each profile. Email taken ONLY from the profile's own "Email" field (PhD students' emails on the same page are ignored). No phone numbers kept. Test on 10: 10/10 emails, all @iimmumbai.ac.in. Full run waits for the user's yes.
- **IIM Bangalore:** the user explicitly allowed AI subagents (Haiku, max 3) for IIMB only, an exception to rule 8. Rules given to them: official iimb.ac.in pages only, emails copied as printed with source link, never guessed, no bypassing blocks. Result: every iimb.ac.in page returned 403 to them too; 0 rows (data/iimb_part1-3.csv are header-only). Next step is the user's choice.
- **"Current database"** = `Profs Database __ Kartik Vuthoo.xlsx`, sheet "IIMs  ISB". New rows get appended there (backup first), with extra columns for research areas and source page.

## 2026-11-19: IIM Bangalore read in a real browser (user's choice)
- The user chose "try a real browser" after the AI agents got 403. The official pages were read in the user's own Chrome (Browser 1): https://www.iimb.ac.in/faculty-list-area-wise -> 11 area pages -> 109 profiles at /user/<id>, 1.5 s apart. No block, no CAPTCHA, nothing bypassed.
- Email = the single mailto link on the professor's own profile. 108/109 have one; Pulak Ghosh's profile shows none. U Dinesh Kumar's profile shows director@iimb.ac.in (Director-in-charge).
- Saved to `data/iimb_browser_read.tsv`; links + emails verified against a fingerprint computed in the browser (109 rows, exact match). The research column holds a short excerpt of each profile's Summary (blank when none).
- Merge into the xlsx (backup in data/): 35 existing IIM B rows confirmed (same email) and given research/source/designation; 2 rows flagged CHECK (Dinesh Kumar, Pulak Ghosh: sheet email not on profile); 15 old rows flagged "not listed on IIMB area faculty pages (may have left)"; 72 new rows appended (rows 425-496). Nothing deleted or overwritten.
- Includes visiting faculty (3 Management Communication, Saras Sarasvathy) and professors of practice, marked in Designation/Added.

## 2026-11-20: IIM A / C / Lucknow verified against official sites; senior's list merged
- Official lists read by plain script (`scripts/scrape_official.py`): IIMA 109 (all with email), IIMC 82 (all), IIML 96 (all; some written as x[dot]y[at]iiml[dot]ac[dot]in). IIML dropped connections once; fetch delay raised to 5 s and errors are no longer cached.
- `scripts/verify_merge.py --write` (backup in data/): 108 confirmed, 25 emails CORRECTED to the official address (old one kept in col H; mostly IIM Lucknow, incl. the three wrong "ashish@iiml"), 3 FILLED (M P Ram Mohan, Prahalad Venkateshan, Akshaya Vijayalakshmi), 37 flagged "not on the official list (may have left)". Nothing deleted.
- Area-chair addresses (chr-...@iima.ac.in) are not used to overwrite a personal email (Viswanath Pingali kept). Rajesh Chandwani (new) only has chr-hrm@ on the official page: flagged CHECK.
- Senior's CSV (Downloads, "Database (Confide) - IIM_ISB"): 44 IIMA/IIMC professors confirmed on official pages and added (rows 497-540); 32 not on official lists skipped; its IIMB part was already superseded by the browser read. Its xlsx copy is identical to the original. ISB ignored (IIMs only).
- Blank-institute IIM Lucknow rows now say "IIM L".
- Not added: official faculty in neither list (IIMA 40, IIMC 13, IIML 54). IIM Kozhikode (63 rows) still unverified.

## 2026-11-20: opening-line style approved
- User approved the style in `opening_lines_samples.md` ("I am deeply fascinated by your work on X and Y ..."), modelled on the user's own example. This replaces the old "no clichés" rule for the opening line.
- Each line: only the professor's own official research text, 2-3 topics in their words, no claims about findings. Subject = "Interest in Research on {first topic}". The user reviews the full list for every batch before sending.

## 2026-11-20: signature and batch size
- Signature: phone number removed; only the email (25B2704@iitb.ac.in) at the end.
- First batch: 15 professors per IIM for IIM A, B, C, Kozhikode, Lucknow and Mumbai (90 emails), best fit first. Kozhikode to be verified against its official site first.
- Signature format (user's example): 'Sincerely,' / name / blank / '--' / name / degree line / institute / email (lowercase).

## 2026-11-20: IIM Kozhikode verified; batch 1 drafted (90)
- IIMK official directory (https://iimk.ac.in/faculty-directory, 9 pages): 116 faculty, 115 emails. xlsx IIMK rows verified (2 corrected incl. a gmail address, 7 flagged may-have-left).
- No-intern notices found on official profiles -> `data/do_not_contact.csv` (8: Soudeep Deb IIMB; Arijit Sen, Chetan Joshi, Suren Sista IIMC; anjana, aghatak, ramesh, Payal Anand IIMK). Excluded from ranking and batches.
- IIMB fuller research text for 48 candidates re-read in Chrome (data/research_iimb.csv).
- Batch 1 = `data/batch.csv` (status draft), 15 each for IIM A, B, C, K, L, Mumbai, written by `scripts/make_batch.py`; review copy `batch_review.md`. All emails come from the official lists.

## 2026-11-24: IITB mail login from programs is blocked
- Webmail works (it now logs in via "Login with SSO"), but the same lowercase login 25b2704 + correct 11-character password is REJECTED by both smtp-auth.iitb.ac.in:587 (535 authentication failed) and imap.iitb.ac.in:993. The servers themselves are up (IMAP needs old TLS settings; scripts handle it).
- Conclusion: since SSO became mandatory, IITB's mail servers do not accept the password from email programs for this account. Needs CC to enable it, or a separate mail-client password. No more login attempts until then (lockout risk).
- Fallback offered: send the approved emails through webmail in the user's Chrome after the user logs in via SSO.
- 2026-11-24 (later): SOLVED. IITB mail servers need the **SSO Access Token** (cc.iitb.ac.in -> How To's -> "How to Replace LDAP Password with SSO Access Token"), not the LDAP/webmail password. Login name 25b2704 (lowercase). Both SMTP and IMAP login tests: LOGIN OK. The GitHub secret IITB_PASSWORD must hold the token (newest token only; no spaces/newlines).
- 2026-11-24: Intro sentence changed to the user's wording: "I am an undergraduate at IIT Bombay, currently pursuing a Minor in AI & Data Science, and I am writing to express my interest in your research." (no name, no CPI in the first line).
- 2026-11-24: Signature no longer repeats the Minor. Extra paragraph "I am eager to apply my data science skills to your quantitative research." added after the project paragraph for 47 professors with quantitative research (column quant_line in data/batch.csv).
- 2026-11-24: User approved all 90 ("approve all 90"); status set to approved.

## 2026-11-24: new sender (tick.yml) replaces send.yml
- User chose option B: the new runner sends batch 1 today. Old send.yml deleted (and its workflow disabled); the 9:30 desktop task was disabled.
- Repo made PUBLIC at the user's request ("I don't care who sees this repo") so Actions minutes are unlimited. Credentials stay in GitHub Secrets: SENDER_EMAIL, SENDER_APP_TOKEN (SSO access token), SMTP_USER.
- All 90 approved rows: send_at = 2026-11-24 09:30 IST. Hard rule: >= 60 s between any two emails (09:30 -> ~11:00).
- Kill switch: data/control.json "sending_enabled" (re-read every minute). Starts false; set true only after the user OKs the dry run.
