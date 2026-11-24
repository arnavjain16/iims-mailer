"""
Batch 2 (90 professors) appended to data/batch.csv as approved, send_at 2026-11-25 08:30 IST.
Lines written from each professor's OWN official research text (research section, profile summary, or
paper titles where the research section is a publication list). Emails/profile links come from the
official lists via data/shortlist.csv, never typed here. Never adds someone already in the batch or on
data/do_not_contact.csv.   python scripts/make_batch2.py
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import send  # noqa: E402

F = "I am deeply fascinated by your work on "
SEND_AT = "2026-11-25 08:30"
Q = "yes"
# (institute, name as on the official list, surname, field, subject topic, rest of line, quant line)
PICKS = [
    # ---- IIM Ahmedabad (16)
    ("IIM A", "Dhiman Bhadra", "Bhadra", "D", "Bayesian Analysis and Biostatistics", "biostatistics and Bayesian analysis, particularly longitudinal and spatial data analysis.", Q),
    ("IIM A", "Satish Deodhar", "Deodhar", "B", "Agricultural Trade and Market Structures", "agricultural trade, imperfectly competitive market structures and micro-finance.", ""),
    ("IIM A", "Nishant Kashyap", "Kashyap", "A", "Financial Intermediation", "financial intermediation.", ""),
    ("IIM A", "Tanmoy Majilla", "Majilla", "B", "Development Economics and Financial Economics", "development economics, financial disclosure and reporting, and financial economics.", ""),
    ("IIM A", "Adrija Majumdar", "Majumdar", "D", "AI and its Business Impact", "the use of AI and its business impact, using natural language processing and econometric techniques.", Q),
    ("IIM A", "Neerav Nagar", "Nagar", "A", "Financial Reporting Quality and Disclosures", "financial reporting quality and disclosures, corporate governance and executive compensation.", ""),
    ("IIM A", "Vivek Pandey", "Pandey", "B", "Development Economics and Financial Inclusion", "development economics and financial inclusion, particularly field experiments and causal machine learning.", Q),
    ("IIM A", "Mehul Raithatha", "Raithatha", "A", "Financial Reporting and Corporate Governance", "financial reporting, corporate governance, and mergers and acquisitions.", ""),
    ("IIM A", "Samrat Roy", "Roy", "D", "Causal Inference and Time Series Models", "causal inference, high-dimensional statistics and advanced time series models.", Q),
    ("IIM A", "Nagarajan Sethuraman", "Sethuraman", "D", "Operational Innovation with Emerging Technologies", "operational innovation with emerging technologies such as AI, and on responsible operations and new product development.", Q),
    ("IIM A", "Kathan Shukla", "Shukla", "D", "Quantitative Methods in Education Research", "applying contemporary quantitative techniques, such as structural equation modeling, to educational problems.", Q),
    ("IIM A", "Anshuman Sinha", "Sinha", "C", "Entrepreneurship and Strategic Change", "entrepreneurship, strategic change and the behavioral theory of the firm.", ""),
    ("IIM A", "Karthik Sriram", "Sriram", "D", "Bayesian Statistics and Data Science", "Bayesian statistics, spatial modeling, change point detection and quantile regression.", Q),
    ("IIM A", "Sandip Chakrabarti", "Chakrabarti", "D", "Transportation Demand Modeling", "transport policy analysis and transportation demand modeling, particularly travel behavior and choice analysis.", Q),
    ("IIM A", "Samrat Gupta", "Gupta", "D", "Network Analytics and Social Media", "network theoretic modelling and analytics, and information disorder driven by social media.", Q),
    ("IIM A", "Amit Karna", "Karna", "C", "Dynamic Capabilities and Diversification", "dynamic capabilities, diversification and strategic leadership.", ""),
    # ---- IIM Bangalore (16) - from the full profile summaries read in Chrome
    ("IIM B", "Shubhabrata Das", "Das", "D", "Statistics and Business Forecasting", "statistics, actuarial mathematics and operations research, particularly business forecasting and insurance analytics.", Q),
    ("IIM B", "Jitamitra Desai", "Desai", "D", "Large-Scale Optimization", "computational decision analytics, particularly large-scale optimization algorithms and their applications in transportation and energy analytics.", Q),
    ("IIM B", "Ananth Krishnamurthy", "Krishnamurthy", "D", "Stochastic Modelling and Supply Chains", "stochastic modelling and optimization techniques and their applications in supply chains, warehousing and logistics.", Q),
    ("IIM B", "Subhabrata Majumdar", "Majumdar", "D", "Trustworthy AI and Statistical Machine Learning", "trustworthy AI and statistical machine learning, particularly the foundations of AI security and alignment.", Q),
    ("IIM B", "Arjun Ramachandra", "Ramachandra", "D", "Optimization under Uncertainty", "optimization under uncertainty, particularly distributionally robust optimization and data-driven tail risk estimation.", Q),
    ("IIM B", "Manaswini Bhalla", "Bhalla", "B", "Information Economics and Pricing", "information economics, particularly issues in pricing, corporate culture and political economy.", ""),
    ("IIM B", "Sarvesh Bandhu", "Bandhu", "B", "Mechanism Design and Platform Economics", "mechanism design, evolutionary game theory and platform economics.", ""),
    ("IIM B", "Tirthatanmoy Das", "Das", "B", "Labour Economics and Econometrics", "labour economics, econometrics and health economics.", Q),
    ("IIM B", "Akhil Ilango", "Ilango", "B", "Industrial Organisation and Digital Platforms", "industrial organisation, particularly how sponsored advertisements on digital platforms affect firms' pricing and competition.", Q),
    ("IIM B", "Gaurav Jakhu", "Jakhu", "B", "Antitrust in Digital Markets", "antitrust and regulatory issues in digital markets.", ""),
    ("IIM B", "Debojyoti Das", "Das", "A", "Accounting and Corporate Finance", "contemporary issues in accounting and corporate finance, including creditors' rights and corporate risk-taking behavior.", ""),
    ("IIM B", "Padmini Srinivasan", "Srinivasan", "A", "Corporate Reporting and Disclosures", "corporate governance and accountability, corporate reporting and disclosures, and sustainability risk management.", ""),
    ("IIM B", "Sreelata Jonnalagedda", "Jonnalagedda", "E", "Market Design and Freemium Pricing", "market design, freemium pricing and digital marketing.", ""),
    ("IIM B", "Mayank Nagpal", "Nagpal", "E", "Marketing Analytics and Machine Learning", "analyzing marketing strategies using data analytics and machine learning techniques.", Q),
    ("IIM B", "Tarun Jain", "Jain", "D", "Strategic Sourcing and Digital Technologies", "strategic sourcing, the management of digital technologies and pricing issues in service supply chains.", ""),
    ("IIM B", "Venu Madhav Tatiparti", "Tatiparti", "A", "Corporate Governance and Board Structure", "corporate governance and board structure.", ""),
    # ---- IIM Calcutta (15)
    ("IIM C", "Megha Sharma", "Sharma", "D", "Large Scale and Stochastic Optimization", "large scale optimization for big data and stochastic optimization.", Q),
    ("IIM C", "Sudhir S. Jaiswall", "Jaiswall", "A", "Executive Compensation and Corporate Governance", "CEO and CFO compensation, management accounting and corporate governance.", ""),
    ("IIM C", "Ramya Tarakad Venkateswaran", "Venkateswaran", "C", "National Culture in International Business", "the influence of national culture in international business, using multilevel quantitative techniques.", Q),
    ("IIM C", "Biswatosh Saha", "Saha", "C", "Strategy as Practice and the Digital Economy", "strategy as practice and the digital economy.", ""),
    ("IIM C", "Latasri Hazarika", "Hazarika", "C", "Strategic Entrepreneurship", "emotion and cognition in entrepreneurship, strategic entrepreneurship and entrepreneurial ecosystems.", ""),
    ("IIM C", "Priya Seetharaman", "Seetharaman", "C", "IT and Digital Strategy", "IT and digital strategy, IT governance and technology adoption.", ""),
    ("IIM C", "Rahul Kumar", "Kumar", "D", "Artificial Intelligence and Data Strategy", "artificial intelligence, data strategy and analytics consulting.", Q),
    ("IIM C", "Saptarshi Purkayastha", "Purkayastha", "C", "Business Groups and Firm Performance", "the effectiveness of business groups, particularly how shifts in macro-economic conditions affect business groups and their affiliated firms' performance.", ""),
    ("IIM C", "Sumanta Basu", "Basu", "D", "Pricing and Revenue Management", "pricing and revenue management, game theoretic applications in business problems and healthcare operations and analytics.", Q),
    ("IIM C", "Samarth Gupta", "Gupta", "B", "Industrial Organization and Financial Inclusion", "industrial organization and financial inclusion.", ""),
    ("IIM C", "Uttam Kumar Sarkar", "Sarkar", "D", "Machine Learning and Social Network Analysis", "machine learning, social networks analysis and discrete optimization.", Q),
    ("IIM C", "Anik Mukherjee", "Mukherjee", "D", "Text Mining and Healthcare Analytics", "location analytics, text mining applications and healthcare analytics.", Q),
    ("IIM C", "Randhir Kumar", "Kumar", "B", "Labour Markets and the Digital Economy", "employment relations, labour markets, global production networks and the digital economy.", ""),
    ("IIM C", "Anupama Kondayya", "Kondayya", "C", "Organizational and Institutional Change", "organizational and institutional change and social evaluations.", ""),
    ("IIM C", "Rajashik Roy Choudhury", "Roy Choudhury", "C", "Careers and Performance Evaluation", "careers, performance evaluation and employee voice.", ""),
    # ---- IIM Kozhikode (17)
    ("IIM K", "Kalpit Sharma", "Sharma", "D", "Economics of Cybersecurity", "cyber-risk issues in information systems and the economics of cybersecurity, using data mining, text mining and machine learning methods.", Q),
    ("IIM K", "Radhakrishna Pillai R", "Pillai", "D", "Digital Transformation and Business Analytics", "digital transformation, disruptive digital technologies and business analytics.", ""),
    ("IIM K", "Salman Ali", "Ali", "C", "Internationalization and Emerging Markets", "the internationalization of firms, strategies in emerging markets and digital transformation strategies.", ""),
    ("IIM K", "Sudershan Kuntluru", "Kuntluru", "A", "Auditing and Earnings Management", "auditing, financial reporting and earnings management, and corporate governance.", ""),
    ("IIM K", "Venkataraman S", "Venkataraman", "C", "Corporate Sustainability and Strategy", "corporate sustainability, the influence of culture on strategy, and entrepreneurship.", ""),
    ("IIM K", "Arqum Mateen", "Mateen", "D", "Digital Transformation and Business Models", "the marketing-operations interface, digital transformation and business model innovation.", ""),
    ("IIM K", "M.K. Nandakumar", "Nandakumar", "C", "Business Model Innovation", "business models and business model innovation, and social and sustainable entrepreneurship.", ""),
    ("IIM K", "Qambar Abidi", "Abidi", "A", "Corporate Bankruptcy and Mutual Funds", "corporate bankruptcy and mutual funds.", ""),
    ("IIM K", "Rupesh Kumar Pati", "Pati", "D", "Sustainable Supply Chains and Digital Strategy", "sustainable supply chains and digital strategy and transformation.", ""),
    ("IIM K", "Akriti Jain", "Jain", "C", "Innovation and Intellectual Property Strategy", "innovation and intellectual property strategy, open innovation and IP models for sustainability transitions.", ""),
    ("IIM K", "Deepak S Kumar", "Kumar", "E", "Image Analytics and Neuro-marketing", "image analytics and neuro-marketing studies.", Q),
    ("IIM K", "Kapil Gupta", "Gupta", "D", "Spatio-Temporal Modelling", "Gaussian processes, spatial statistics and spatio-temporal modelling, particularly house price dynamics.", Q),
    ("IIM K", "Nemiraja Jadiyappa", "Jadiyappa", "A", "Capital Structure and Earnings Management", "capital structuring decisions, earnings management and accounting conservatism.", ""),
    ("IIM K", "Nycil George", "George", "C", "Behavioural Strategy and Competitive Dynamics", "behavioural strategy, competitive dynamics and organizational capabilities.", ""),
    ("IIM K", "Shaphali Gupta", "Gupta", "E", "Marketing Strategy and Customer Experience", "marketing strategy, emerging market strategies and customer experience management.", ""),
    ("IIM K", "Shovan Chowdhury", "Chowdhury", "D", "Statistical Learning and Healthcare Analytics", "reliability theory, statistical learning and interpretable machine learning, and healthcare analytics.", Q),
    ("IIM K", "Soumya Roy", "Roy", "D", "Statistical Inference and Applied Machine Learning", "frequentist and Bayesian statistical inference, reliability and survival analysis, and applied machine learning.", Q),
    # ---- IIM Lucknow (18)
    ("IIM L", "Ajay Kumar Garg", "Garg", "A", "Earnings Management and Capital Structure", "earnings management, public issues, capital structure and value creating restructuring.", ""),
    ("IIM L", "Amita Mital", "Mital", "C", "Strategic Alliances and Joint Ventures", "strategy formulation and implementation, and strategic alliances and joint ventures.", ""),
    ("IIM L", "Arunabha Mukhopadhyay", "Mukhopadhyay", "D", "Cyber-risk Modelling", "cyber-risk management, particularly quantitative techniques for cyber-risk modelling and cyber-risk insurance.", Q),
    ("IIM L", "Ashwani Kumar", "Kumar", "D", "Predictive Analytics and Data Mining", "predictive analytics and data mining, data science for business and machine learning algorithms.", Q),
    ("IIM L", "Priyanshu Gupta", "Gupta", "A", "Impact Investing and Social Entrepreneurship", "environment and development, impact investing and social entrepreneurship.", ""),
    ("IIM L", "Sushant Kumar", "Kumar", "E", "Green Consumption", "green consumption, including your meta-analytic study of green consumption across borders.", ""),
    ("IIM L", "Ashutosh Kumar Sinha", "Sinha", "A", "Mergers and Acquisitions", "mergers and acquisitions, particularly M&A premia, merger motives and cross-border acquisitions by Indian firms.", ""),
    ("IIM L", "Jalaj Pathak", "Pathak", "A", "Sentiment and Emerging Stock Markets", "the impact of sentiment on emerging stock markets.", Q),
    ("IIM L", "Kaushik Ranjan Bandyopadhyay", "Bandyopadhyay", "B", "Carbon Taxes and Sustainable Urban Policy", "the effectiveness of carbon taxes for urban passenger transportation and of direct benefit transfers.", ""),
    ("IIM L", "Utsav Pandey", "Pandey", "D", "Optimization and Data Envelopment Analysis", "optimization techniques, performance evaluation using data envelopment analysis and machine learning.", Q),
    ("IIM L", "Deepak Prajapati", "Prajapati", "D", "Reliability and Bayesian Inference", "reliability theory and survival analysis, Bayesian inference and computational statistics.", Q),
    ("IIM L", "Kartik Yadav", "Yadav", "B", "Development Economics and Micro-econometrics", "development economics and micro-econometrics, particularly education, health and migration.", Q),
    ("IIM L", "Samir K Srivastava", "Srivastava", "D", "Public Procurement and Data Analytics", "public procurement, including your study of e-procurement's impact on procurement performance using data analytics.", Q),
    ("IIM L", "Seshadev Sahoo", "Sahoo", "A", "Initial Public Offerings", "initial public offerings and financial reporting and analysis.", ""),
    ("IIM L", "Garima Mittal", "Mittal", "D", "Portfolio Optimization", "optimization techniques, multiple criteria decision making and portfolio optimization.", Q),
    ("IIM L", "Divya Choudhary", "Choudhary", "D", "Sustainable Operations and Risk Management", "sustainable operations management, supply chain risk management and the circular economy.", ""),
    ("IIM L", "Sabyasachi Sinha", "Sinha", "C", "Corporate Entrepreneurship and Innovation", "corporate entrepreneurship and innovation, and new venture creation and growth.", ""),
    ("IIM L", "Ashutosh Jha", "Jha", "D", "Diffusion and Adoption of Information Systems", "the diffusion and adoption of information systems and the techno-economics of next generation mobile networks.", ""),
    # ---- IIM Mumbai (8) - only professors whose 'Area of Research' section is filled in
    ("IIM Mumbai", "B. KOTESWARARAO NAIK", "Naik", "C", "Technology and Innovation Management", "the management of intellectual property, technology and innovation management, and patent analytics.", ""),
    ("IIM Mumbai", "Jasashwi Mandal", "Mandal", "D", "Maritime Shipping and Logistics", "maritime shipping and logistics, operations research and machine learning.", Q),
    ("IIM Mumbai", "Maheswar Singha Mahapatra", "Mahapatra", "D", "Supply Chain Optimization", "supply chain optimization, sustainable operations and multi-objective optimization.", Q),
    ("IIM Mumbai", "Milind Akarte", "Akarte", "D", "Smart and Additive Manufacturing", "smart manufacturing, additive manufacturing and manufacturing strategy.", ""),
    ("IIM Mumbai", "Vidyadhar V. Gedam", "Gedam", "A", "Circular Economy and ESG", "sustainable development for business, the circular economy and ESG.", ""),
    ("IIM Mumbai", "Padmanav Acharya", "Acharya", "D", "Multimodal and Reverse Logistics", "multimodal and reverse logistics, and system dynamics simulation and optimisation.", ""),
    ("IIM Mumbai", "Rauf Iqbal", "Iqbal", "D", "Ergonomics and Human Factors", "ergonomics and human factors engineering, and work system design.", ""),
    ("IIM Mumbai", "Ravindra Gokhale", "Gokhale", "D", "Production Planning and Transportation Logistics", "production planning and control, and transportation logistics.", ""),
]


def main():
    rows = list(csv.DictReader((ROOT / "data" / "batch.csv").open(encoding="utf-8-sig")))
    have = {r["email"] for r in rows}
    dnc = {r["profile_url"] for r in csv.DictReader((ROOT / "data" / "do_not_contact.csv").open(encoding="utf-8-sig"))}
    short = {(r["institute"], r["name"]): r for r in csv.DictReader((ROOT / "data" / "shortlist.csv").open(encoding="utf-8-sig"))}
    new = []
    for inst, name, surname, field, topic, rest, quant in PICKS:
        s = short.get((inst, name))
        if not s:
            raise SystemExit(f"not on the official list: {inst} {name}")
        if s["email"] in have or s["profile_url"] in dnc or s["email"].startswith(("chr-", "director", "dean")):
            raise SystemExit(f"already emailed / do-not-contact / role address: {inst} {name}")
        have.add(s["email"])
        r = {"name": name.title() if name.isupper() else name, "surname": surname, "institute": inst,
             "email": s["email"], "field": field, "subject_topic": topic, "opening_line": F + rest,
             "quant_line": quant, "profile_url": s["profile_url"], "status": "approved", "send_at": SEND_AT}
        send.render(r)
        new.append(r)
    send.save(rows + new)
    from collections import Counter
    print(len(new), "added for", SEND_AT, dict(Counter(r["institute"] for r in new)))


if __name__ == "__main__":
    main()
