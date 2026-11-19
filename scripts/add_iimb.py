"""
Turns the IIM Bangalore browser read (data/iimb_raw.json) into data/iim_bangalore.csv
and appends NEW professors to the xlsx sheet "IIMs  ISB".

Why a browser: iimb.ac.in answers scripts with 403, so the official pages were read in
the user's own Chrome (allowed by the user, 2026-11-19). Every email below is the single
mailto link printed on that professor's own iimb.ac.in profile page. Nothing is guessed.

  python scripts/add_iimb.py            build the CSV and show what would be added
  python scripts/add_iimb.py --write    also append to the xlsx (make a backup first)
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "iimb_browser_read.tsv"
OUT = ROOT / "data" / "iim_bangalore.csv"
XLSX = ROOT / "Profs Database __ Kartik Vuthoo.xlsx"
COLUMNS = ["name", "institute", "area", "designation", "email", "email_note", "research_interests", "profile_url"]
TITLES = ("professor", "lecturer", "director", "dean", "chair")


def squash(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def build_rows():
    # data/iimb_browser_read.tsv: one row per profile read in Chrome on 2026-11-19.
    # Links + emails were checked against a fingerprint computed in the browser (109 rows, exact match).
    # summary_start is a short excerpt of the profile's Summary (blank when the profile has none).
    rows = []
    for r in csv.DictReader(RAW.open(encoding="utf-8"), delimiter="\t"):
        email = r["email"].strip()
        note = ""
        if not email:
            note = "no email on profile"
        elif email.lower() == "director@iimb.ac.in":
            note = "Director's office address (he is the Director-in-charge)"
        elif "visiting" in r["designation"].lower():
            note = "visiting faculty"
        rows.append({"name": r["name"], "institute": "IIM B", "area": r["area"], "designation": r["designation"],
                     "email": email, "email_note": note, "research_interests": r["summary_start"],
                     "profile_url": "https://www.iimb.ac.in/user/" + r["user"]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    rows = build_rows()
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} IIMB profiles -> {OUT} ({sum(1 for r in rows if r['email'])} with one clear email)")

    wb = openpyxl.load_workbook(XLSX)
    ws = wb["IIMs  ISB"]
    old_emails, old_names = {}, {}
    for i in range(2, ws.max_row + 1):
        name, email, inst = ws.cell(i, 1).value, ws.cell(i, 3).value, ws.cell(i, 4).value
        if email:
            old_emails[str(email).strip().lower()] = i
        if name and (inst in (None, "IIM B")):
            old_names.setdefault(squash(name), i)

    new, matched, differ, seen_rows = [], [], [], set()
    for r in rows:
        hit = old_emails.get(r["email"].lower()) if r["email"] else None
        by_name = old_names.get(squash(r["name"]))
        if hit:
            matched.append((hit, r))
            seen_rows.add(hit)
        elif by_name and ws.cell(by_name, 4).value == "IIM B":
            differ.append((by_name, r))
            seen_rows.add(by_name)
        else:
            new.append(r)
    print(f"Already in the sheet with the same email: {len(matched)}")
    print(f"In the sheet by name but email differs: {len(differ)}")
    for i, r in differ:
        print(f"   {r['name']}: sheet has {ws.cell(i, 3).value}, official profile has {r['email'] or '(none)'}")
    gone = [i for i in range(2, ws.max_row + 1) if ws.cell(i, 4).value == "IIM B" and i not in seen_rows]
    print(f"IIM B rows in the sheet NOT found on today's IIMB faculty pages: {len(gone)}")
    for i in gone:
        print(f"   row {i}: {ws.cell(i, 1).value} <{ws.cell(i, 3).value}>")
    print(f"New professors to add: {len(new)}")

    if not args.write:
        return
    # Existing rows: only fill the new, empty columns (E-H). Name/dept/email are never overwritten.
    for i, r in matched:
        extra = [r["research_interests"], r["profile_url"], r["designation"], "2026-11-19 email confirmed on official IIMB profile"]
        for c, v in enumerate(extra, 5):
            if ws.cell(i, c).value in (None, ""):
                ws.cell(i, c, v)
    for i, r in differ:
        msg = f"2026-11-19 CHECK: official profile shows {r['email'] or 'no email'}; sheet email not on the profile"
        for c, v in enumerate([r["research_interests"], r["profile_url"], r["designation"], msg], 5):
            if ws.cell(i, c).value in (None, ""):
                ws.cell(i, c, v)
    for i in gone:
        if ws.cell(i, 8).value in (None, ""):
            ws.cell(i, 8, "2026-11-19 CHECK: not listed on IIMB area faculty pages (may have left)")
    last = max(i for i in range(1, ws.max_row + 1) if any(ws.cell(i, c).value for c in range(1, 5)))
    for r in new:
        last += 1
        vals = [r["name"], r["area"], r["email"], "IIM B", r["research_interests"], r["profile_url"],
                r["designation"], "2026-11-19 browser read (official site)" + (f"; {r['email_note']}" if r["email_note"] else "")]
        for c, v in enumerate(vals, 1):
            ws.cell(last, c, v)
    wb.save(XLSX)
    print(f"Appended {len(new)} rows; last row is now {last}.")


if __name__ == "__main__":
    main()
