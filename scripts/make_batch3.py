"""Batch 3: 10 IIM Lucknow + 10 IIM Kozhikode, send_at 2026-11-25 14:01 IST (user: 'in 14 mins').
Lines from each professor's own official research text; emails from the official lists."""
import csv, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import send
F = "I am deeply fascinated by your work on "
AT = "2026-11-25 14:01"
Q = "yes"
PICKS = [
    ("IIM K", "Leena Mary Eapen", "Eapen", "B", "Energy Economics", "energy economics, macroeconomic policies and development economics.", ""),
    ("IIM K", "Sthanu R Nair", "Nair", "B", "Public Finance and Indian Economic Policy", "public finance, Indian economic policy and agricultural sector policy.", ""),
    ("IIM K", "Chitwan Lalji", "Lalji", "B", "Applied Microeconomics", "applied microeconomics, health economics and development economics.", Q),
    ("IIM K", "Shubhasis Dey", "Dey", "B", "Economics of Information and Political Economy", "the economics of information and political economy, and development and labour economics.", ""),
    ("IIM K", "Kausik Gangopadhyay", "Gangopadhyay", "B", "Applied Economics", "applied economics, particularly labour economics and development economics.", Q),
    ("IIM K", "Salamah Ansari", "Ansari", "B", "Sovereign Debt Restructuring", "sovereign debt restructuring and climate change politics.", ""),
    ("IIM K", "Srikanth Krishnaprasad", "Krishnaprasad", "D", "Sharing Economy and Sustainable Operations", "the sharing economy, sustainable operations management and on-demand service systems.", ""),
    ("IIM K", "Swati Jain", "Jain", "D", "Cyber-Risk Management", "cyber-risk management, cybersecurity data analytics and IT governance.", Q),
    ("IIM K", "Dharun Kasilingam", "Kasilingam", "E", "Technology and Consumer Behavior", "technology and consumer behavior, and unstructured data analytics.", Q),
    ("IIM K", "Ashutosh Sarkar", "Sarkar", "D", "Supply Chain Management and Optimization", "supply chain management, procurement and applied optimization.", Q),
    ("IIM L", "Dipti Gupta", "Gupta", "A", "India's Low Carbon Development Pathways", "India's low carbon development pathways, including your recent book Framing India's Low Carbon Development Pathways.", ""),
    ("IIM L", "Debdatta Pal", "Pal", "B", "Empirical Energy Economics", "empirical energy economics, applied agricultural economics and choice modelling.", Q),
    ("IIM L", "Sanjeet Singh", "Singh", "D", "Data Envelopment Analysis and Environmental Efficiency", "data envelopment analysis, environmental efficiency and mathematical modelling.", Q),
    ("IIM L", "Sushil Kumar (ABM Area)", "Kumar", "C", "Climate Change and Business Strategies", "corporate social responsibility and stakeholder management, and climate change and business strategies.", ""),
    ("IIM L", "Kaustav Banerjee", "Banerjee", "D", "Statistical Inference", "statistical inference and biostatistics.", Q),
    ("IIM L", "Arvind Shroff", "Shroff", "D", "Platform Operations and Revenue Management", "service and healthcare operations, online platform operations, and pricing and revenue management.", Q),
    ("IIM L", "Kshitij Awasthi", "Awasthi", "C", "Corporate Political Activities", "corporate political activities, particularly how government connections affect firms' business performance.", ""),
    ("IIM L", "Chandan Sharma", "Sharma", "B", "Infrastructure, R&D and Productivity", "how public infrastructure, R&D, trade and technology transfer affect firm productivity.", Q),
    ("IIM L", "Suresh Kumar Jakhar", "Jakhar", "D", "Mechanism Design and Sustainable Networks", "mechanism design, game theory and sustainable network design.", Q),
    ("IIM L", "Priyatam Anurag", "Anurag", "C", "Regulation and Corporate Governance", "incentive theory, the regulation and governance of multi-objective corporations, and firm responses to public interest regulation.", ""),
]
rows = list(csv.DictReader((ROOT / "data" / "batch.csv").open(encoding="utf-8-sig")))
have = {r["email"] for r in rows}
dnc = {r["profile_url"] for r in csv.DictReader((ROOT / "data" / "do_not_contact.csv").open(encoding="utf-8-sig"))}
short = {(r["institute"], r["name"]): r for r in csv.DictReader((ROOT / "data" / "shortlist.csv").open(encoding="utf-8-sig"))}
new = []
for inst, name, sur, field, topic, rest, q in PICKS:
    s = short[(inst, name)]
    assert s["email"] not in have and s["profile_url"] not in dnc, name
    have.add(s["email"])
    r = {"name": re.sub(r"\s*\(.*?\)", "", name), "surname": sur, "institute": inst, "email": s["email"], "field": field,
         "subject_topic": topic, "opening_line": F + rest, "quant_line": q, "profile_url": s["profile_url"],
         "status": "approved", "send_at": AT}
    send.render(r); new.append(r)
send.save(rows + new)
print(len(new), "added for", AT)
