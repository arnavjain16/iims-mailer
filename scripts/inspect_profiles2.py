"""Step 3b: look closer at the IIMA and IIML directory markup (facts only, nothing stored)."""
import re, sys
from pathlib import Path
from urllib.parse import urljoin
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup
from common import fetch

for name, url, needle in [("IIMA", "https://www.iima.ac.in/faculty-research/faculty-directory", "Strategy"),
                          ("IIML", "https://www.iiml.ac.in/faculty-profile", "Ajay Singh")]:
    soup = BeautifulSoup(fetch(url)["text"], "html.parser")
    print("=" * 60, name)
    hit = soup.find(string=re.compile(needle))
    if hit:
        el = hit.parent
        for _ in range(3):
            el = el.parent
        print(str(el)[:900])
    anchors = [(a.get_text(" ", strip=True), urljoin(url, a["href"])) for a in soup.select("li a, .views-row a, td a") if a.get_text(strip=True)]
    print("anchors in lists:", len(anchors))
    for t, u in anchors[40:52]:
        print("   ", t[:35], "->", u)
