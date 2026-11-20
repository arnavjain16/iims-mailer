"""
Saves each professor's research text, copied from their OWN official profile page,
so every email opening line can be checked against its source.

  IIMA: "Research Area" section          IIML: the "Research" tab (fallback: "Overview")
  IIMC: text after "Research Interest(s)" on /users/<id> (free text, so a window is kept)

Output: data/research_<inst>.csv  (profile_url, research_text)
Mumbai and Bangalore research text is already in data/iim_mumbai.csv and data/iim_bangalore.csv.

  python scripts/collect_research.py iima iiml iimc
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup  # noqa: E402
from common import PROJECT, fetch  # noqa: E402

SRC = {"iima": "iim_ahmedabad.csv", "iimc": "iim_calcutta.csv", "iiml": "iim_lucknow.csv"}
STOP = r"(Books?/Book Chapters|Publications|Journal Articles|Teaching|Education|Awards|Conference|Working Papers|Courses|Selected)"


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def items(el):
    lis = [clean(li.get_text(" ")) for li in el.find_all("li")]
    return "; ".join(x for x in lis if x) or clean(el.get_text(" "))


def iima(soup):
    for h in soup.find_all("h2"):
        if clean(h.get_text()).lower() == "research area":
            sec = h.find_parent("section")
            if sec:
                return re.sub(r"^Research Area\s*", "", items(sec))
    return ""


def iiml(soup):
    for key in ("Research", "Overview"):
        el = soup.find(id=key)
        if el and clean(el.get_text(" ")):
            return items(el)
    return ""


def iimc(soup):
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    text = clean(soup.get_text(" "))
    m = re.search(r"(Research Interests?|Areas? of Interest|Research Areas?)\s*:?\s*(.{0,700})", text, re.I)
    if not m:
        return ""
    return re.split(STOP, m.group(2))[0].strip()[:500]


def main():
    readers = {"iima": iima, "iiml": iiml, "iimc": iimc}
    for key in sys.argv[1:] or readers:
        rows = list(csv.DictReader((PROJECT / "data" / SRC[key]).open(encoding="utf-8-sig")))
        out = []
        for i, r in enumerate(rows, 1):
            page = fetch(r["profile_url"])
            text = readers[key](BeautifulSoup(page["text"], "html.parser")) if page["status"] == 200 else ""
            out.append({"profile_url": r["profile_url"], "name": r["name"], "research_text": text[:600]})
            if i % 20 == 0:
                print(f"  {key} {i}/{len(rows)}", flush=True)
        path = PROJECT / "data" / f"research_{key}.csv"
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["profile_url", "name", "research_text"])
            w.writeheader()
            w.writerows(out)
        print(f"{key}: {sum(1 for o in out if o['research_text'])}/{len(out)} with research text -> {path.name}", flush=True)


if __name__ == "__main__":
    main()
