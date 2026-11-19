"""
Review and approve the startup database.

  python scripts/manage.py export                 -> startups.xlsx + review.md + drafts_preview.md
  python scripts/manage.py approve --ready        -> every company with a chosen email becomes 'approved'
  python scripts/manage.py approve --names "Jupiter,Dhan"
  python scripts/manage.py skip --names "Zepto"   -> never email these
  python scripts/manage.py set-email --name "Dhan" --email careers@dhan.co
  python scripts/manage.py replied --name "Jupiter" --note "asked for a call"
  python scripts/manage.py status
  python scripts/manage.py log                    -> sent_log.csv
"""
import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from template import render  # noqa: E402

DB_PATH = ROOT / "startups.db"


def names_arg(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def export(con):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    con.row_factory = sqlite3.Row
    rows = con.execute("""SELECT * FROM companies ORDER BY (city='Mumbai') DESC,
                          (chosen_email IS NULL), track, name""").fetchall()
    wb = Workbook()
    ws = wb.active
    ws.title = "Startups"
    cols = ["name", "city", "mumbai_on_site", "sector", "track", "chosen_email", "chosen_category",
            "chosen_source", "status", "sent_at", "followup_sent_at", "careers_url", "apply_url", "home_url",
            "what", "notes"]
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E78")
    for r in rows:
        ws.append([r[c] for c in cols])
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = {"name": 24, "chosen_email": 32, "what": 50}.get(c, 18)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

    ws2 = wb.create_sheet("All emails found")
    ws2.append(["company", "email", "category", "on company domain", "found on page"])
    for e in con.execute("""SELECT c.name, e.email, e.category, e.domain_match, e.source_url
                            FROM emails e JOIN companies c ON c.id=e.company_id ORDER BY c.name, e.category"""):
        ws2.append(list(e))
    ws2.column_dimensions["A"].width = 24
    ws2.column_dimensions["B"].width = 36
    ws2.column_dimensions["E"].width = 60
    wb.save(ROOT / "startups.xlsx")

    # review.md
    lines = ["# Startup list for review", "",
             "Every address below is printed on the company's own website (page shown). Nothing is guessed.", ""]
    with_email = [r for r in rows if r["chosen_email"]]
    without = [r for r in rows if not r["chosen_email"]]
    lines.append(f"**{len(with_email)} companies with a usable address** "
                 f"({sum(1 for r in with_email if r['city'] == 'Mumbai')} in Mumbai); "
                 f"{len(without)} without one (apply on their careers page instead).")
    lines.append("")
    lines.append("| # | Company | City | Track | Email | Type | Found on |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(with_email, 1):
        lines.append(f"| {i} | {r['name']} | {r['city']} | {r['track']} | {r['chosen_email']} | "
                     f"{r['chosen_category']} | {r['chosen_source']} |")
    lines += ["", "## No usable address found (apply via careers page)", "",
              "| Company | City | Careers / apply link | Note |", "|---|---|---|---|"]
    for r in without:
        link = r["apply_url"] or r["careers_url"] or r["home_url"] or ""
        lines.append(f"| {r['name']} | {r['city']} | {link} | {r['notes'] or ''} |")
    (ROOT / "review.md").write_text("\n".join(lines), encoding="utf-8")

    # one sample draft per track
    out = ["# Draft emails, one per track", ""]
    seen = set()
    for r in with_email:
        if r["track"] in seen:
            continue
        seen.add(r["track"])
        subject, body = render(r["name"], r["track"], r["what"], r["city"])
        out += [f"## Track: {r['track']} (example: {r['name']} -> {r['chosen_email']})", "",
                f"**Subject:** {subject}", "", "```", body.strip(), "```", ""]
    (ROOT / "drafts_preview.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote startups.xlsx, review.md, drafts_preview.md  ({len(with_email)} with email, {len(without)} without)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "approve", "skip", "set-email", "replied", "status", "log"])
    ap.add_argument("--names", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--email", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--ready", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB_PATH)

    if a.cmd == "export":
        export(con)
    elif a.cmd == "approve":
        if a.ready:
            n = con.execute("UPDATE companies SET status='approved' WHERE status='new' AND chosen_email IS NOT NULL").rowcount
        else:
            n = sum(con.execute("UPDATE companies SET status='approved' WHERE name=? AND chosen_email IS NOT NULL "
                                "AND status IN ('new','skip')", (x,)).rowcount for x in names_arg(a.names))
        print(f"Approved {n}")
    elif a.cmd == "skip":
        n = sum(con.execute("UPDATE companies SET status='skip' WHERE name=? AND status!='sent'", (x,)).rowcount
                for x in names_arg(a.names))
        print(f"Skipped {n}")
    elif a.cmd == "set-email":
        con.execute("UPDATE companies SET chosen_email=?, chosen_category='manual', chosen_source='set by user' "
                    "WHERE name=?", (a.email.strip().lower(), a.name))
        print("Updated")
    elif a.cmd == "replied":
        con.execute("UPDATE companies SET status='replied', reply=? WHERE name=?", (a.note, a.name))
        print("Marked replied")
    elif a.cmd == "log":
        import csv
        with open(ROOT / "sent_log.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["company", "city", "email", "status", "sent_at_ist", "followup_sent_at_ist"])
            w.writerows(con.execute("""SELECT name, city, chosen_email, status, sent_at, followup_sent_at
                                       FROM companies WHERE status IN ('sent','replied','bounced')
                                       ORDER BY sent_at"""))
        print("Wrote sent_log.csv")
    elif a.cmd == "status":
        for row in con.execute("SELECT status, COUNT(*), SUM(chosen_email IS NOT NULL) FROM companies GROUP BY status"):
            print(f"{row[0]:<10} {row[1]:>4} companies ({row[2]} with email)")
    con.commit()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
