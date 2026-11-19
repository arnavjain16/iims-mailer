"""
Step 1 of Phase 1: look at candidate faculty-directory pages and report what each one is like.
It only downloads (politely, cached) and prints facts: status, title, number of links,
how many links look like professor profiles, and any robots.txt block.
It does not collect or guess any professor data.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup
from common import fetch

CANDIDATES = {
    "IIM Ahmedabad": ["https://www.iima.ac.in/faculty-research/faculty-directory",
                      "https://www.iima.ac.in/faculty"],
    "IIM Bangalore": ["https://www.iimb.ac.in/faculty-directory",
                      "https://www.iimb.ac.in/faculty"],
    "IIM Calcutta": ["https://www.iimcal.ac.in/faculty",
                     "https://www.iimcal.ac.in/faculty-research/faculty"],
    "IIM Lucknow": ["https://www.iiml.ac.in/faculty",
                    "https://www.iiml.ac.in/faculty-research/faculty"],
}

for institute, urls in CANDIDATES.items():
    print("=" * 70)
    print(institute)
    for url in urls:
        r = fetch(url)
        if r.get("blocked_by_robots"):
            print(f"  {url}\n    BLOCKED by robots.txt")
            continue
        soup = BeautifulSoup(r["text"], "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else "(no title)"
        links = soup.find_all("a", href=True)
        prof_like = [a for a in links if re.search(r"faculty|profile|people|prof", a["href"], re.I)]
        print(f"  {url}\n    status={r['status']} cached={r['from_cache']} final={r.get('final_url')}")
        print(f"    title={title[:90]!r} size={len(r['text'])} chars, links={len(links)}, profile-like links={len(prof_like)}")
        for a in prof_like[:5]:
            print("      e.g.", a.get_text(strip=True)[:40], "->", a["href"][:90])
