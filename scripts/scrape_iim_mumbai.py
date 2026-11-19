"""
IIM Mumbai faculty scraper (Phase 1).

Reads ONLY the official site iimmumbai.ac.in:
  1. the faculty directory  https://iimmumbai.ac.in/faculty?page=N   (name, area, designation, profile link)
  2. each professor's profile page                                   (email, research areas)

Rules kept:
  * The email is taken ONLY from the "Email" field at the top of the professor's own
    profile page. Emails of their PhD students, printed lower on the same page, are ignored.
  * Nothing is guessed. If the Email field is empty, the email column stays blank.
  * Phone numbers are NOT collected.
  * Pages are fetched politely (2 s apart, robots.txt respected) and cached (see common.py).

Usage (from the cold-mailer folder):
  python scripts/scrape_iim_mumbai.py --limit 10     test: first 10 professors only
  python scripts/scrape_iim_mumbai.py                everyone
Output: data/iim_mumbai.csv  (test runs write data/iim_mumbai_test.csv)
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup  # noqa: E402
from common import PROJECT, fetch  # noqa: E402

BASE = "https://iimmumbai.ac.in/faculty"
PROFILE_RE = re.compile(r"^https://iimmumbai\.ac\.in/faculty/profile/(\d+)$")
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
COLUMNS = ["name", "institute", "area", "designation", "email", "email_note",
           "research_interests", "profile_url"]


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def read_directory():
    """All professors listed in the directory, in page order, without duplicates."""
    people, seen, page = [], set(), 1
    while page <= 30:                                   # safety stop
        r = fetch(f"{BASE}?page={page}")
        if r["status"] != 200:
            print(f"  directory page {page}: status {r['status']}, stopping")
            break
        soup = BeautifulSoup(r["text"], "html.parser")
        new = 0
        for tr in soup.find_all("tr"):
            a = tr.find("a", href=PROFILE_RE)
            cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
            if not a or len(cells) < 4 or a["href"] in seen:
                continue
            seen.add(a["href"])
            new += 1
            name = re.sub(r"^(Prof\.|Dr\.)\s*", "", clean(a.get_text(" ")))
            people.append({"name": name, "area": cells[2], "designation": cells[3], "profile_url": a["href"]})
        print(f"  directory page {page}: {new} new")
        if new == 0:
            break
        page += 1
    return people


def field(soup, label):
    """Value next to an <h6>label</h6> in the profile's top card."""
    for h in soup.find_all("h6"):
        if clean(h.get_text()).lower() == label.lower():
            row = h.find_parent("div", class_="row")
            val = row.find("div", class_="col-sm-9") if row else None
            return clean(val.get_text(" ")) if val else ""
    return ""


def section_items(soup, section_id):
    box = soup.find(id=section_id)
    if not box:
        return ""
    items = [clean(li.get_text(" ")) for li in box.find_all("li")]
    if not items:
        items = [clean(p.get_text(" ")) for p in box.find_all("p")]
    items = [i for i in items if i and not i.lower().startswith(("research areas", "subject areas"))]
    return "; ".join(items)[:300]


def read_profile(person):
    r = fetch(person["profile_url"])
    if r["status"] != 200:
        return {"email": "", "email_note": f"profile status {r['status']}", "research_interests": ""}
    soup = BeautifulSoup(r["text"], "html.parser")
    email = field(soup, "Email")
    note = ""
    if not email:
        note = "no email on profile"
    elif not EMAIL_RE.match(email):
        note, email = f"unusual email text: {email!r}", ""
    elif not email.lower().endswith("@iimmumbai.ac.in"):
        note = "not an iimmumbai.ac.in address (as printed on profile)"
    area = field(soup, "Area & Groups") or person["area"]
    research = section_items(soup, "area_of_research") or section_items(soup, "interest")
    return {"email": email, "email_note": note, "research_interests": research, "area": area}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only the first N professors (test run)")
    args = ap.parse_args()

    print("Reading the directory...")
    people = read_directory()
    print(f"{len(people)} professors listed.")
    if args.limit:
        people = people[:args.limit]

    rows = []
    for i, p in enumerate(people, 1):
        p.update(read_profile(p))
        p["institute"] = "IIM Mumbai"
        rows.append(p)
        print(f"[{i}/{len(people)}] {p['name']:<40} {p['email'] or '-':<35} {p['email_note']}")

    out_dir = PROJECT / "data"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / ("iim_mumbai_test.csv" if args.limit else "iim_mumbai.csv")
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with_email = sum(1 for r in rows if r["email"])
    print(f"\nSaved {len(rows)} rows ({with_email} with email) to {out}")


if __name__ == "__main__":
    main()
