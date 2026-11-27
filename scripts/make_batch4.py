"""Batch 4: 10 IIM Kozhikode + 10 IIM Lucknow, send_at 2026-11-27 10:48 IST (user: "in 15 mins").
Lines from each professor's own official research text; emails from the official lists."""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import send  # noqa: E402

F = "I am deeply fascinated by your work on "
AT = "2026-11-27 10:48"
Q = "yes"
PICKS = [
    ("IIM K", "Rajesh Srinivas Upadhyayula", "Upadhyayula", "C", "Industrial Clusters and Emerging Market Multinationals", "corporate governance, industrial clusters and capabilities, and emerging market multinationals.", ""),
    ("IIM K", "Sumit Mitra", "Mitra", "C", "Open Innovation and Social Entrepreneurship", "corporate governance, open innovation and social entrepreneurship, including women entrepreneurship.", ""),
    ("IIM K", "Deepak Dhayanithy", "Dhayanithy", "C", "Strategy and Analytics", "strategy and analytics, with applications in sport, health and the environment.", Q),
    ("IIM K", "Mohammed Shahid Abdulla", "Abdulla", "D", "Multi-Criteria Decision Making and Machine Learning", "multi-criteria decision making and machine learning.", Q),
    ("IIM K", "Satish Krishnan", "Krishnan", "D", "ICT for Sustainable Development", "the dark side of technology, e-government and ICT for sustainable development.", ""),
    ("IIM K", "Vidushi Pandey", "Pandey", "D", "Platform Business and Citizen Participation", "social media and citizen participation, gamification and platform business.", ""),
    ("IIM K", "Gladys Stephen", "Stephen", "E", "Responsible Consumption", "responsible consumption and cause-related marketing.", ""),
    ("IIM K", "Sanchar Sarkar", "Sarkar", "B", "Environmental Communication", "environmental communication, particularly climate change and the human footprint.", ""),
    ("IIM K", "S. Subramanian", "Subramanian", "C", "Corporate Governance and Competitiveness", "corporate governance, competitiveness and international business.", ""),
    ("IIM K", "Priya Narayanan", "Narayanan", "E", "Consumer Perceptions and Influencers", "consumer perceptions, affect and cognition, particularly brands, influencers and AI in Indian markets.", ""),
    ("IIM L", "Maya Kant Awasthi", "Awasthi", "B", "Food Quality Signaling and Information Asymmetry", "food quality signaling, market information asymmetry and land valuation.", ""),
    ("IIM L", "Sanjeev Kapoor", "Kapoor", "B", "Rural Finance and Agriculture", "rural finance, agro-processing and irrigation management, and agricultural diversification.", ""),
    ("IIM L", "Tamalika Koley", "Koley", "D", "Survival Analysis and Applied Statistics", "survival analysis, reliability theory and applied statistics.", Q),
    ("IIM L", "Veethica Smriti", "Smriti", "C", "Technological Positioning and Firm Knowledge", "optimal distinctiveness, technological positioning and how firm knowledge shapes invention performance.", ""),
    ("IIM L", "Himanshu Rathore", "Rathore", "D", "Mechanism Design and Combinatorial Optimisation", "mechanism design, combinatorial optimisation, metaheuristics and network analysis.", Q),
    ("IIM L", "Shalabh Singh", "Singh", "D", "Multi-objective Decision Making and Drone Logistics", "multi-objective decision making, multi-choice programming, and transportation and drone logistics.", Q),
    ("IIM L", "Sonia Singh", "Singh", "D", "Combinatorial Optimization and Network Flows", "combinatorial optimization, network flow problems and multi-objective decision making.", Q),
    ("IIM L", "Sampa Anupurba Pahi", "Pahi", "E", "Responsible and Ethical Marketing", "responsible and ethical marketing, brand and consumer activism, and influencer marketing.", ""),
    ("IIM L", "Gaurav Garg", "Garg", "D", "Linear and Measurement Error Models", "linear models, measurement error models and restricted regression.", Q),
    ("IIM L", "Amit Agrahari", "Agrahari", "D", "Generative AI and the Future of Work", "generative AI and the future of work, including your study of customer experience on a ride-hailing application.", ""),
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
    send.render(r)
    new.append(r)
send.save(rows + new)
print(len(new), "added for", AT)
