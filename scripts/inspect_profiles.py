"""
Step 3 of Phase 1: open ONE sample profile page per IIM and print what is on it,
so we know where the research areas and the email are printed. Facts only.
"""
import re, sys
from pathlib import Path
from urllib.parse import urljoin
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup
from common import fetch

SPECS = {
 "IIM Ahmedabad": ("https://www.iima.ac.in/faculty-research/faculty-directory", r"/faculty-research/(?!centers|areas|faculty-directory|research|faculty$)[^/]+$"),
 "IIM Calcutta": ("https://www.iimcal.ac.in/faculty/faculty-directory", r"/users/"),
 "IIM Lucknow": ("https://www.iiml.ac.in/faculty-profile", r"iiml\.ac\.in/[a-z0-9\-]+$"),
}
EMAIL = re.compile(r"[\w.\-]+\s*(?:@|\[at\]|\(at\))\s*[\w.\-]+", re.I)

for name, (dir_url, pat) in SPECS.items():
    print("=" * 70, "\n", name)
    soup = BeautifulSoup(fetch(dir_url)["text"], "html.parser")
    seen, links = set(), []
    for a in soup.find_all("a", href=True):
        u = urljoin(dir_url, a["href"]).split("#")[0]
        if re.search(pat, u) and u not in seen and a.get_text(strip=True):
            seen.add(u); links.append((a.get_text(" ", strip=True)[:40], u))
    print("  candidate profile links:", len(links))
    for t, u in links[:6]:
        print("    ", t, "->", u)
    if not links:
        continue
    t, u = links[1] if len(links) > 1 else links[0]
    r = fetch(u)
    s = BeautifulSoup(r["text"], "html.parser")
    for tag in s(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", s.get_text(" ", strip=True))
    print("  SAMPLE PROFILE:", t, u, "status", r["status"], "len", len(text))
    print("  emails/at-patterns found:", EMAIL.findall(text)[:3], "|", [m.group(0) for m in EMAIL.finditer(text)][:3])
    for kw in ("Research Interest", "Research Area", "Area of Interest", "Areas of Interest", "Interests", "Specialization", "Expertise"):
        i = text.find(kw)
        if i >= 0:
            print(f"  '{kw}' ->", text[i:i+220])
            break
    else:
        print("  no obvious research-interest label; start of page text:", text[:300])
