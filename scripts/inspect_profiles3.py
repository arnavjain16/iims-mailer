"""Step 3c: IIMA area page + one IIML profile page (facts only, nothing stored)."""
import re, sys
from pathlib import Path
from urllib.parse import urljoin
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup
from common import fetch

def clean(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "nav", "footer", "header"]):
        t.decompose()
    return re.sub(r"\s+", " ", s.get_text(" ", strip=True))

# IIMA: an academic-area page should list its professors
u = "https://www.iima.ac.in/faculty-research/areas/Finance-and-Accounting"
r = fetch(u); s = BeautifulSoup(r["text"], "html.parser")
print("IIMA area page", r["status"], len(r["text"]))
links = [(a.get_text(" ", strip=True), urljoin(u, a["href"])) for a in s.find_all("a", href=True)]
people = [l for l in links if re.search(r"/faculty-research/(faculty|people|profile)|/faculty/|/profile/", l[1])]
print(" people-like links:", len(people)); [print("   ", t[:30], "->", h) for t, h in people[:6]]
print(" text sample:", clean(r["text"])[:400])

# IIML: one profile
u = "https://www.iiml.ac.in/faculty-data?n=MTM="
r = fetch(u); t = clean(r["text"])
print("\nIIML profile", r["status"], len(t))
print(" emails:", re.findall(r"[\w.\-]+\s*(?:@|\[at\]|\(at\))\s*[\w.\- \[\]dot]+", t)[:3])
for kw in ("Research Interest", "Area", "Specialization", "Interest"):
    i = t.find(kw)
    if i >= 0:
        print(f" '{kw}' ->", t[max(0,i-60):i+260]); break
else:
    print(" start:", t[:400])
