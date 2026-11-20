"""
Verify the database's IIM A / IIM C / IIM Lucknow rows against the OFFICIAL lists
(data/iim_ahmedabad.csv, iim_calcutta.csv, iim_lucknow.csv from scrape_official.py),
and add the senior's professors (Downloads CSV) only when the official page confirms them.

For each existing row of these institutes:
  CONFIRMED   email is on the official list           -> fill empty cols E-H (research/source/designation/added)
  CORRECTED   name on official list, email different  -> email replaced by the official one; old one kept in col H
  FILLED      name on official list, row had no email -> official email written
  NOT LISTED  not on the official list                -> flagged in col H (may have left / visiting); nothing deleted
Senior rows: added only if on the official list and not already in the sheet; others are reported and skipped.

  python scripts/verify_merge.py            report only
  python scripts/verify_merge.py --write    apply (make a backup first)
"""
import argparse
import csv
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "Profs Database __ Kartik Vuthoo.xlsx"
SENIOR = Path("C:/Users/ARNAV JAIN/Downloads/random/random/Database (Confide) - IIM_ISB copy.csv")
OFFICIAL = {"IIM A": "iim_ahmedabad.csv", "IIM C": "iim_calcutta.csv", "IIM L": "iim_lucknow.csv", "IIM K": "iim_kozhikode.csv"}
SENIOR_INST = {"IIM Ahemdabad": "IIM A", "IIM Calcutta": "IIM C"}
TODAY = "2026-11-20"


def _base(s):
    return re.sub(r"\(.*?\)|(prof|dr)\.?", " ", (s or "").lower())    # drop "(OM Area)", "Prof.", "Dr."


def sq(s):
    return re.sub(r"[^a-z]", "", _base(s))


def tokens(s):
    return frozenset(t for t in re.split(r"[^a-z]+", _base(s)) if len(t) > 1)


def load_official(code):
    rows = list(csv.DictReader((ROOT / "data" / OFFICIAL[code]).open(encoding="utf-8-sig")))
    by_email = {r["email"]: r for r in rows if r["email"]}
    by_name = {sq(r["name"]): r for r in rows}
    by_tok = {tokens(r["name"]): r for r in rows}
    return rows, by_email, by_name, by_tok


def find(off, name, email):
    _, by_email, by_name, by_tok = off
    if email and email in by_email:
        return by_email[email], "email"
    r = by_name.get(sq(name)) or by_tok.get(tokens(name))
    return (r, "name") if r else (None, None)


def load_senior():
    inst, out = None, []
    for row in csv.reader(SENIOR.open(encoding="utf-8-sig")):
        row = (row + ["", "", ""])[:3]
        if row[0] and not row[1] and not row[2]:
            inst = row[0].strip()
            continue
        if row[0] == "Professor" or not any(row) or inst not in SENIOR_INST:
            continue
        out.append({"inst": SENIOR_INST[inst], "name": row[0].strip(), "area": row[1].strip(), "email": row[2].strip().lower()})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    wb = openpyxl.load_workbook(XLSX)
    ws = wb["IIMs  ISB"]
    off = {code: load_official(code) for code in OFFICIAL}
    report = {k: [] for k in ("CONFIRMED", "CORRECTED", "FILLED", "NOT LISTED")}
    used = {code: set() for code in OFFICIAL}          # official profile urls already in the sheet

    for i in range(2, ws.max_row + 1):
        name, email, inst = ws.cell(i, 1).value, str(ws.cell(i, 3).value or "").strip().lower(), ws.cell(i, 4).value
        if not name or name == "Prof Name":
            continue
        if inst is None and email.endswith("@iiml.ac.in"):
            inst = "IIM L"
            if args.write:
                ws.cell(i, 4, "IIM L")                 # user confirmed: blank institute = IIM Lucknow
        if inst not in OFFICIAL:
            continue
        o, how = find(off[inst], name, email)
        # a shared email (e.g. three 'ashish@iiml') only counts for the person whose NAME matches
        if o and how == "email" and sq(o["name"]) != sq(name) and tokens(o["name"]) != tokens(name):
            o2, how2 = find((None, {}, off[inst][2], off[inst][3]), name, "")
            o, how = (o2, how2) if o2 else (None, None)
        if not o:
            report["NOT LISTED"].append((i, inst, name, email))
            if args.write and ws.cell(i, 8).value in (None, ""):
                ws.cell(i, 8, f"{TODAY} CHECK: not on the official {inst} faculty list (may have left)")
            continue
        used[inst].add(o["profile_url"])
        if o["email"].startswith("chr-") and email:
            kind, note = "CONFIRMED", f"{TODAY} kept: official page shows only the area-chair address {o['email']}"
        elif o["email"] and email == o["email"]:
            kind, note = "CONFIRMED", f"{TODAY} email confirmed on official {inst} page"
        elif o["email"] and email:
            kind, note = "CORRECTED", f"{TODAY} email corrected from {email} to the official {o['email']}"
        elif o["email"]:
            kind, note = "FILLED", f"{TODAY} email filled from official {inst} page"
        else:
            kind, note = "NOT LISTED", f"{TODAY} CHECK: on official list but no email printed"
        report[kind].append((i, inst, name, email, o["email"]))
        if args.write:
            if kind in ("CORRECTED", "FILLED"):
                ws.cell(i, 3, o["email"])
            for c, v in ((6, o["profile_url"]), (7, o["designation"]), (8, note)):
                if kind in ("CORRECTED", "FILLED") and c == 8:
                    ws.cell(i, c, v)                   # always record a change
                elif ws.cell(i, c).value in (None, ""):
                    ws.cell(i, c, v)

    # senior rows
    add, skipped = [], []
    for s in load_senior():
        o, _ = find(off[s["inst"]], s["name"], s["email"])
        if not o:
            skipped.append(s)
        elif o["profile_url"] not in used[s["inst"]] and o["email"]:
            used[s["inst"]].add(o["profile_url"])
            add.append(o)

    for k, v in report.items():
        print(f"\n{k}: {len(v)}")
        if k != "CONFIRMED":
            for x in v:
                print("   row", *x)
    print(f"\nSenior rows confirmed on official pages and NEW to the sheet: {len(add)}")
    for o in add:
        print(f"   + {o['institute']} {o['name']} <{o['email']}> ({o['area']})")
    print(f"Senior rows NOT on the official lists (skipped): {len(skipped)}")
    for s in skipped:
        print(f"   - {s['inst']} {s['name']} <{s['email'] or '-'}>")
    for code in OFFICIAL:
        rest = [r for r in off[code][0] if r["profile_url"] not in used[code] and r["email"]]
        print(f"Official {code} faculty in NEITHER list (not added): {len(rest)}")

    if args.write:
        last = max(i for i in range(1, ws.max_row + 1) if any(ws.cell(i, c).value for c in range(1, 5)))
        for o in add:
            last += 1
            for c, v in enumerate([o["name"], o["area"], o["email"], o["institute"], "", o["profile_url"],
                                   o["designation"], f"{TODAY} from senior's list; email confirmed on official page"], 1):
                ws.cell(last, c, v)
        wb.save(XLSX)
        print(f"\nSaved. Last row is now {last}.")


if __name__ == "__main__":
    main()
