"""
Ranks verified professors (IIM A, B, C, Lucknow, Mumbai) by how well their OFFICIAL research text
matches Arnav's resume projects, and suggests which project paragraph (A-E) fits.
This is only a shortlist for the user to choose from; nothing is sent from here.

Inputs: data/iim_*.csv (official lists) + data/research_*.csv (official research text).
Output: data/shortlist.csv  (rank within institute, score, matched keywords, research text)

  python scripts/rank_fit.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

# keyword -> weight. Taken from what the resume actually covers.
KEYWORDS = {
    r"financ": 3, r"valuation": 3, r"capital market": 3, r"corporate finance": 3, r"asset pricing": 3,
    r"portfolio": 3, r"derivative": 3, r"risk": 2, r"banking|bank\b": 2, r"fintech|payment|upi|cbdc|digital currenc|crypto": 4,
    r"monetary": 2, r"invest": 2, r"accounting|financial reporting|earnings": 2, r"equity": 2,
    r"sustainab|esg|green|climate": 2, r"quantitative|econometric|time series|forecast|statistic": 3,
    r"machine learning|artificial intelligence|\bai\b|data science|analytics|data": 2, r"optimi[sz]ation": 1,
    r"strateg": 2, r"platform|digital": 2, r"entrepreneur|start-?up|venture": 2, r"behavio[u]?ral": 1,
    r"emerging econom|india": 1, r"macroeconom|international finance|capital flow": 2, r"market": 1,
}
FIELD_RULES = [  # first match wins -> project paragraph A-E
    ("D", r"quantitative|time series|forecast|statistic|decision science|operations|optimi|analytics|data science|machine learning|derivative|portfolio"),
    ("A", r"financ|accounting|valuation|capital market|banking|invest|asset pricing|sustainab|esg"),
    ("B", r"econom|policy|monetary|development"),
    ("E", r"marketing|consumer|pricing|brand"),
    ("C", r"strateg|entrepreneur|management|platform"),
]


def score(text):
    t = text.lower()
    hits = [k for k in KEYWORDS if re.search(k, t)]
    return sum(KEYWORDS[k] for k in hits), [re.sub(r"[\\\[\]|?]+.*", "", k) for k in hits]


def field_for(text):
    t = text.lower()
    for f, pat in FIELD_RULES:
        if re.search(pat, t):
            return f
    return "C"


def read(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig"))) if path.exists() else []


def main():
    dnc = {r["profile_url"] for r in read(D / "do_not_contact.csv")}
    people = []
    for inst_file, research_file, inst in [("iim_ahmedabad.csv", "research_iima.csv", "IIM A"),
                                           ("iim_calcutta.csv", "research_iimc.csv", "IIM C"),
                                           ("iim_lucknow.csv", "research_iiml.csv", "IIM L"),
                                           ("iim_kozhikode.csv", "research_iimk.csv", "IIM K"),
                                           ("iim_bangalore.csv", "research_iimb.csv", "IIM B"),
                                           ("iim_mumbai.csv", None, "IIM Mumbai")]:
        res = {r["profile_url"]: r["research_text"] for r in read(D / research_file)} if research_file else {}
        for r in read(D / inst_file):
            if r["profile_url"] in dnc:
                continue                                   # profile says: no internship requests
            if not r["email"] or r.get("email_note", "").startswith(("visiting", "Director")):
                continue
            if "visiting" in r.get("designation", "").lower():
                continue
            research = res.get(r["profile_url"]) or r.get("research_interests", "") or ""
            s, hits = score(r["area"] + " " + research)
            people.append({"institute": inst, "name": r["name"], "email": r["email"], "area": r["area"],
                           "designation": r.get("designation", ""), "score": s, "matched": ", ".join(hits),
                           "field": field_for(r["area"] + " " + research), "research_text": research[:400],
                           "profile_url": r["profile_url"]})
    out = []
    for inst in ("IIM A", "IIM B", "IIM C", "IIM K", "IIM L", "IIM Mumbai"):
        group = sorted([p for p in people if p["institute"] == inst], key=lambda p: -p["score"])
        for i, p in enumerate(group, 1):
            p["rank"] = i
            out.append(p)
        print(f"{inst}: {len(group)} professors; top 5:",
              "; ".join(f"{p['name']} ({p['score']})" for p in group[:5]))
    cols = ["institute", "rank", "score", "name", "area", "designation", "email", "field", "matched",
            "research_text", "profile_url"]
    with (D / "shortlist.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(f"Saved {len(out)} rows -> data/shortlist.csv")


if __name__ == "__main__":
    main()
