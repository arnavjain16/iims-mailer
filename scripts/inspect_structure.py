"""
Step 2 of Phase 1: look at HOW each directory and one sample profile page is built.
Prints facts only (link patterns, whether an email or research text appears on a profile).
No professor data is stored or guessed here.
"""
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup
from common import fetch

DIRECTORIES = {
    "IIM Ahmedabad": "https://www.iima.ac.in/faculty-research/faculty-directory",
    "IIM Calcutta": "https://www.iimcal.ac.in/faculty/faculty-directory",
    "IIM Lucknow (directory)": "https://www.iiml.ac.in/faculty-profile",
    "IIM Lucknow (by area)": "https://www.iiml.ac.in/faculty-list-by-area",
}

EMAIL_HINT = re.compile(r"[\w.\-]+\s*(@|\[at\]|\(at\)|\bat\b)\s*[\w.\-]+\s*(\.|\[dot\]|\(dot\)|\bdot\b)\s*(ac|in|edu|com)", re.I)

for name, url in DIRECTORIES.items():
    print("=" * 70)
    print(name, url)
    r = fetch(url)
    print("  status", r["status"], "robots-blocked" if r.get("blocked_by_robots") else "", "size", len(r["text"]))
    if r["status"] != 200:
        continue
    soup = BeautifulSoup(r["text"], "html.parser")
    links = [(a.get_text(" ", strip=True), urljoin(url, a["href"])) for a in soup.find_all("a", href=True)]
    # which URL "shapes" appear most often (professor profile links usually share one shape)
    shapes = Counter(re.sub(r"[^/]+$", "*", l[1].split("?")[0]) for l in links)
    print("  most common link shapes:")
    for shape, n in shapes.most_common(6):
        print(f"    {n:4d}  {shape}")
    print("  does the page text itself mention a table or list of names? tables:", len(soup.find_all("table")),
          "| list items:", len(soup.find_all("li")))
