"""
Reads the OFFICIAL faculty lists of IIM Ahmedabad, IIM Calcutta and IIM Lucknow
(plain script, polite + cached via common.py) and saves one CSV per institute in data/.
These CSVs are the reference used to verify every email in the database.

  IIMA: https://www.iima.ac.in/faculty-research/faculty-directory?page=0..N  -> each profile ("Email :")
  IIMC: https://www.iimcal.ac.in/faculty/faculty-directory   (name, department, mailto on one page)
  IIML: https://www.iiml.ac.in/faculty-profile               -> each profile ("E-mail : x[at]iiml[dot]ac[dot]in")

Nothing is guessed: an email is kept only when printed for that professor on the official page.

  python scripts/scrape_official.py iima iimc iiml
"""
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup  # noqa: E402
from common import PROJECT, fetch  # noqa: E402

COLUMNS = ["name", "institute", "area", "designation", "email", "email_note", "profile_url"]
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
TITLE_RE = re.compile(r"((?:Distinguished |Visiting |Adjunct |Associate |Assistant )?Professor(?: of Practice)?|Faculty)", re.I)


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def deobfuscate(s):
    s = re.sub(r"\s*[\[\(]\s*at\s*[\]\)]\s*", "@", s, flags=re.I)
    return re.sub(r"\s*[\[\(]\s*dot\s*[\]\)]\s*", ".", s, flags=re.I).strip().lower()


def text_of(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return clean(s.get_text(" "))


def iima():
    base = "https://www.iima.ac.in/faculty-research/faculty-directory"
    people, seen, page = [], set(), 0
    while page < 40:
        r = fetch(f"{base}?field_designation_target_id=All&title=&field_primary_area_target_id=&page={page}")
        soup = BeautifulSoup(r["text"], "html.parser")
        new = 0
        for a in soup.select("a.faculty-card-box"):
            url = urljoin(base, a["href"])
            if url in seen:
                continue
            seen.add(url)
            new += 1
            ps = [clean(p.get_text(" ")) for p in a.find_all("p")]
            people.append({"name": ps[0] if ps else "", "area": ps[1] if len(ps) > 1 else "", "profile_url": url})
        print(f"  IIMA directory page {page}: {new} new")
        if new == 0:
            break
        page += 1
    rows = []
    for i, p in enumerate(people, 1):
        r = fetch(p["profile_url"])
        soup = BeautifulSoup(r["text"], "html.parser")
        email = ""
        for para in soup.select(".employee-contact-detail p"):
            t = clean(para.get_text(" "))
            if t.lower().startswith("email"):
                email = deobfuscate(t.split(":", 1)[1])
        area = p["area"]
        box = soup.select_one(".employee-area-box p")
        if box:
            area = clean(box.get_text(" ")).split(":", 1)[-1].strip() or area
        m = TITLE_RE.search(text_of(r["text"])[:3000])
        rows.append(finish(p["name"], "IIM A", area, m.group(1) if m else "", email, p["profile_url"], "@iima.ac.in"))
        if i % 20 == 0:
            print(f"  IIMA profiles {i}/{len(people)}")
    return rows


def iimc():
    url = "https://www.iimcal.ac.in/faculty/faculty-directory"
    soup = BeautifulSoup(fetch(url)["text"], "html.parser")
    rows = []
    for box in soup.select("div.faculty-dir-box"):
        name = clean(box.select_one(".views-field-field-name").get_text(" ")) if box.select_one(".views-field-field-name") else ""
        dept_el = box.select_one(".views-field-field-academic-group .field-content")
        mail_el = box.select_one(".views-field-mail a[href^=mailto]")
        user_el = box.select_one(".views-field-name a[href]")
        pop_el = box.select_one(".views-field-field-pop .field-content")
        email = mail_el["href"].split(":", 1)[1].strip().lower() if mail_el else ""
        rows.append(finish(name, "IIM C", clean(dept_el.get_text(" ")) if dept_el else "",
                           clean(pop_el.get_text(" ")) if pop_el else "", email,
                           urljoin(url, user_el["href"]) if user_el else url, "@iimcal.ac.in"))
    print(f"  IIMC directory: {len(rows)} entries")
    return rows


def iiml():
    url = "https://www.iiml.ac.in/faculty-profile"
    soup = BeautifulSoup(fetch(url)["text"], "html.parser")
    people = {}
    for a in soup.find_all("a", href=re.compile(r"faculty-data\?n=")):
        u = urljoin(url, a["href"])
        name = re.sub(r"^((Noida Campus|Lucknow Campus|On Leave)\s*)+", "", clean(a.get_text(" ")))
        if name and u not in people:
            people[u] = name
    rows = []
    for i, (u, name) in enumerate(people.items(), 1):
        r = fetch(u)
        t = text_of(r["text"])
        # the professor's own address is the mailto inside the profile's "contact" list
        cs = BeautifulSoup(r["text"], "html.parser").select_one("ul.contact")
        mail = cs.select_one("a[href^=mailto]") if cs else None
        email = deobfuscate(mail["href"].split(":", 1)[1]) if mail else ""
        if not email:   # fallback: the "E-mail :" line printed in the page text
            m = re.search(r"E-?mail\s*:\s*([\w.\[\]+-]+?\s*(?:@|\[at\])\s*iiml\s*(?:\.|\[dot\])\s*ac\s*(?:\.|\[dot\])\s*in)", t, re.I)
            email = deobfuscate(m.group(1)) if m else ""
        k = t.find(name)
        head = t[k + len(name): k + len(name) + 200] if k >= 0 else ""
        dm = re.match(r"\s*(.*?Professor(?: of Practice)?|Faculty[^ ]*)\s+(.*?)\s+Overview", head)
        rows.append(finish(name, "IIM L", dm.group(2) if dm else "", dm.group(1) if dm else "", email, u, "@iiml.ac.in"))
        if i % 20 == 0:
            print(f"  IIML profiles {i}/{len(people)}")
    return rows


def iimk():
    base = "https://iimk.ac.in/faculty-directory"
    rows, seen, page = [], set(), 1                      # pages are numbered from 1
    while page < 30:
        soup = BeautifulSoup(fetch(f"{base}?page={page}")["text"], "html.parser")
        new = 0
        for a in soup.select("div.fac-bg > a[href]"):
            url = urljoin(base, a["href"])
            if url in seen:
                continue
            seen.add(url)
            new += 1
            parts = [x for x in (clean(s) for s in a.stripped_strings) if x and x != "View More"]
            raw = next((b.get("title", "") for b in a.find_all("button") if "@" in b.get("title", "")), "")
            mails = [m.strip().lower() for m in raw.split(",") if "@" in m]
            personal = [m for m in mails if not re.match(r"(dean|chair|director|head|office)[-_.]", m)]
            email = (personal or mails or [""])[0]
            rows.append(finish(parts[0].title() if parts else "", "IIM K", parts[1] if len(parts) > 1 else "",
                               "", email, url, "@iimk.ac.in"))
        print(f"  IIMK directory page {page}: {new} new")
        if new == 0:
            break
        page += 1
    return rows


def finish(name, inst, area, desig, email, url, domain):
    note = ""
    if not email:
        note = "no email on official page"
    elif not EMAIL_RE.match(email):
        note, email = f"unusual email text: {email!r}", ""
    elif not email.endswith(domain):
        note = "not an institute address (as printed)"
    return {"name": clean(name), "institute": inst, "area": clean(area), "designation": clean(desig),
            "email": email, "email_note": note, "profile_url": url}


def main():
    readers = {"iima": (iima, "iim_ahmedabad"), "iimc": (iimc, "iim_calcutta"), "iiml": (iiml, "iim_lucknow"),
               "iimk": (iimk, "iim_kozhikode")}
    for key in sys.argv[1:] or readers:
        fn, fname = readers[key]
        print(f"Reading {key}...")
        rows = fn()
        out = PROJECT / "data" / f"{fname}.csv"
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
        print(f"  saved {len(rows)} rows ({sum(1 for r in rows if r['email'])} with email) -> {out.name}")


if __name__ == "__main__":
    main()
