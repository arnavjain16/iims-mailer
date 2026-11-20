"""
Builds data/batch.csv (status=draft) for batch 1: 15 professors per IIM (A, B, C, K, L, Mumbai).
Each opening line was written from that professor's OWN official research text
(data/research_*.csv, data/iim_mumbai.csv, data/research_iimb.csv) in the user's approved style.
Email + profile link are taken from the official lists, never typed here.
Also writes batch_review.md so the user can read every line next to its source.

  python scripts/make_batch.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
F = "I am deeply fascinated by your work on "

# (institute, name exactly as on the official list, surname used in "Dear Professor X", field A-E, subject topic, rest of opening line)
PICKS = [
    # ---------------- IIM Ahmedabad
    ("IIM A", "Joshy Jacob", "Jacob", "A", "Pricing of Financial Assets", "the pricing of financial assets and the influence of behavioral issues in asset returns and corporate finance."),
    ("IIM A", "Prashant Das", "Das", "A", "Commercial Real Estate and Valuation", "commercial real estate, household finance and valuation."),
    ("IIM A", "Balagopal Gopalakrishnan", "Gopalakrishnan", "A", "Corporate Finance and Banking", "corporate finance, banking and financial intermediation."),
    ("IIM A", "Ajay Pandey", "Pandey", "A", "Capital Markets and Corporate Finance", "capital markets, corporate finance and corporate governance."),
    ("IIM A", "Swetha Agarwal", "Agarwal", "A", "Accounting Information in Capital Markets", "the role of accounting information in capital markets and the pricing of corporate debt."),
    ("IIM A", "Abhiman Das", "Das", "D", "Monetary Economics and Time Series Analysis", "monetary economics and on applied econometrics and time series analysis."),
    ("IIM A", "Sumeet Rajput", "Rajput", "A", "Disclosure Regulation and Corporate Governance", "the role of accounting information in capital markets and the economic consequences of disclosure regulation and corporate governance."),
    ("IIM A", "Ellapulli Vasudevan", "Vasudevan", "D", "Behavioral Finance", "behavioral finance, particularly retail investor behavior, and on the low volatility anomaly and factor models."),
    ("IIM A", "Ankur Sinha", "Sinha", "D", "Artificial Intelligence and Financial Text Mining", "business intelligence and artificial intelligence, and on natural language processing and financial text mining."),
    ("IIM A", "Sanket Mohapatra", "Mohapatra", "B", "International Finance and Global Capital Flows", "international finance and global capital flows, particularly corporate financing patterns in emerging economies."),
    ("IIM A", "Arindam Banerjee", "Banerjee", "E", "Econometric Modelling of Customer Response", "the econometric modelling of customer response to marketing mix variables in retail environments."),
    ("IIM A", "Arnab Kumar Laha", "Laha", "D", "Robust Statistics and Data Analytics", "robust statistics, commodities market models and data analytics in marketing."),
    ("IIM A", "Avani Desai", "Desai", "A", "Investor Relations and Behavioural Finance", "investor relations and corporate reputation, and on corporate finance and behavioural finance."),
    ("IIM A", "Anusha Reddy", "Reddy", "E", "the Marketing-Finance Interface", "marketing strategy and the marketing-finance interface."),
    ("IIM A", "Anand Kumar Jaiswal", "Jaiswal", "E", "Artificial Intelligence in Marketing", "applications of artificial intelligence in marketing and on business model innovations."),
    # ---------------- IIM Bangalore
    ("IIM B", "Sankarshan Basu", "Basu", "D", "Option Pricing and Portfolio Valuation", "option pricing, bond and portfolio valuation, and applications of quantitative techniques to finance."),
    ("IIM B", "Shashidhar Murthy", "Murthy", "D", "Asset Pricing", "asset pricing and investor heterogeneity, particularly your current projects on liquidity, credit risk and volatility."),
    ("IIM B", "Ashok Thampy", "Thampy", "A", "Corporate Finance and Financial Risk Management", "corporate finance, financial risk management and banking."),
    ("IIM B", "Anand Deo", "Deo", "D", "Financial Engineering and Data-Driven Optimisation", "statistics, applied probability and financial engineering, particularly data-driven optimisation models that perform robustly in the presence of extreme risks."),
    ("IIM B", "Kuldeep Singh", "Singh", "B", "Quantitative Macroeconomics", "quantitative macroeconomic models for developing economies, particularly the impact of financial frictions on development."),
    ("IIM B", "Anirudh Dhawan", "Dhawan", "A", "Behavioral Finance and Cryptocurrencies", "behavioral finance and financial markets, particularly your research on cryptocurrencies."),
    ("IIM B", "Raja Reddy Bujunoori", "Bujunoori", "B", "Financial Intermediation and Monetary Policy", "information economics, financial intermediation and monetary policy."),
    ("IIM B", "Nitin Vishen", "Vishen", "A", "Banking and Household Finance", "banking and financial intermediation, particularly the finances of low-income households and the interaction between firms and banks."),
    ("IIM B", "Sumit Saurav", "Saurav", "D", "Asset Pricing and Options", "asset pricing, options and banking."),
    ("IIM B", "Srinivasan Rangan", "Rangan", "A", "Financial Analysis and Valuation", "market efficiency, financial analysis and valuation, and initial public offerings."),
    ("IIM B", "V. Ravi Anshuman", "Anshuman", "A", "Market Microstructure and Capital Markets", "market microstructure, capital markets and corporate financial management issues in emerging markets."),
    ("IIM B", "Varun Jindal", "Jindal", "A", "Empirical Corporate Finance", "empirical corporate finance, particularly mergers and acquisitions and seasoned equity offerings."),
    ("IIM B", "Chetan Subramanian", "Subramanian", "B", "Monetary Economics and Financial Markets", "monetary economics, financial markets and international macroeconomics."),
    ("IIM B", "Anubha Agarwal", "Agarwal", "B", "Firm Dynamics and Economic Growth", "firm dynamics, innovation and economic growth, particularly the interplay between firm cash holdings, mergers and acquisitions, and growth."),
    ("IIM B", "Sachin Sridhar", "Sridhar", "E", "Consumer Behavior on Digital Platforms", "extracting behavioral insights from consumer activity on digital platforms using statistical and machine learning methods."),
    # ---------------- IIM Calcutta
    ("IIM C", "Ankit Kumar", "Kumar", "D", "Macro-Finance and Quantitative Modelling", "macro-finance and quantitative modelling, particularly your use of AI methods alongside Bayesian time-series econometrics."),
    ("IIM C", "Arpita Ghosh", "Ghosh", "A", "Financial Reporting and Corporate Sustainability", "corporate financial reporting and financial statement analysis, and on CSR and corporate sustainability."),
    ("IIM C", "Vivek Rajvanshi", "Rajvanshi", "D", "Trading Strategies and Market Microstructure", "trading strategies, high-frequency trading and market microstructure."),
    ("IIM C", "Arnab Bhattacharya", "Bhattacharya", "A", "Corporate Finance and Market Microstructure", "corporate finance and market microstructure."),
    ("IIM C", "Sahadeb Sarkar", "Sarkar", "D", "Business Forecasting and Financial Market Models", "business forecasting, financial market models and business analytics."),
    ("IIM C", "Sudarshan Kumar", "Kumar", "D", "Fixed Income and Quantitative Finance", "fixed income, macro-finance and quantitative finance."),
    ("IIM C", "Samit Paul", "Paul", "D", "Volatility and VaR Modeling", "volatility and VaR modeling, portfolio management and risk management."),
    ("IIM C", "Manisha Chakrabarty", "Chakrabarty", "B", "Applied Econometrics and Applied Finance", "applied econometrics, development economics and applied finance."),
    ("IIM C", "Sudhakara Reddy", "Reddy", "A", "Liquidity and Algorithmic Trading", "market microstructure, especially liquidity and algorithmic trading, and the pricing of initial public offerings."),
    ("IIM C", "Manju Jaiswall", "Jaiswall", "A", "Financial Statement Analysis", "financial statement analysis, mergers and acquisitions, and debt financing."),
    ("IIM C", "V K Unni", "Unni", "B", "Capital Market Regulations", "capital market regulations, including the Takeover Code and IPO regulations."),
    ("IIM C", "Saravana Jaikumar L.", "Jaikumar", "E", "Data-Driven Marketing and Business Analytics", "data-driven marketing, business analytics and consumer welfare, with a focus on emerging markets and digital transformation."),
    ("IIM C", "Abhipsa Pal", "Pal", "B", "Mobile Payment Usage", "mobile payment usage and technology usage models."),
    ("IIM C", "Prajamitra Bhuyan", "Bhuyan", "D", "Statistical Data Science", "statistical data science and methodology motivated by real-life challenges in complex systems, social science and public policy."),
    ("IIM C", "Ayesha Arora", "Arora", "D", "Digital Supply Chain Management", "digital supply chain management, data sharing in supply chains and generative AI pricing."),
    # ---------------- IIM Kozhikode
    ("IIM K", "Sony Thomas", "Thomas", "D", "Asset Pricing and Portfolio Management", "asset pricing, portfolio management and derivatives."),
    ("IIM K", "Abhinav Anand", "Anand", "D", "Financial Economics and Quantitative Finance", "financial economics and game theory, particularly corporate finance, asset pricing and quantitative finance."),
    ("IIM K", "Aravind Sampath", "Sampath", "A", "Market Microstructure and Asset Pricing", "market microstructure, financial markets and asset pricing."),
    ("IIM K", "Jijo Lukose P J", "Lukose", "A", "Empirical Corporate Finance and Asset Pricing", "empirical corporate finance and empirical asset pricing."),
    ("IIM K", "Abhilash S Nair", "Nair", "D", "Asset Pricing Models", "asset pricing models, market microstructure and regulatory economics."),
    ("IIM K", "Aswin Alora", "Alora", "A", "Equity Valuation", "financial markets and instruments, equity valuation and supply chain finance."),
    ("IIM K", "Ekta Sikarwar", "Sikarwar", "A", "Exchange Rate Risk and International Finance", "exchange rate risk exposure, central bank intervention and international finance."),
    ("IIM K", "Joffi Thomas", "Thomas", "E", "Sustainability Oriented Marketing", "sustainability oriented marketing, customer trust and brand equity."),
    ("IIM K", "Rachappa Shette", "Shette", "A", "Quality of Earnings", "the quality of earnings and financial performance evaluation."),
    ("IIM K", "Sidhartha S Padhi", "Padhi", "D", "Supply Chain Risk Management and Supply Chain Finance", "supply chain risk management, operations strategy and sustainability, and supply chain finance."),
    ("IIM K", "Ashok Thomas", "Thomas", "A", "Savings and Portfolio Decisions", "savings and portfolio decisions, financial literacy and socially responsible investment."),
    ("IIM K", "Mridul Kumar Saggar", "Saggar", "B", "Monetary Policy and International Finance", "monetary policy and monetary operations, international finance and financial inclusion."),
    ("IIM K", "Pankaj Kumar Baag", "Baag", "A", "Credit Risk in Banks", "credit risk in banks, financial inclusion and corporate governance in banks."),
    ("IIM K", "Rudra Sensarma", "Sensarma", "B", "Macroeconomics and Banking", "macroeconomics, banking and applied econometrics."),
    ("IIM K", "Saparya Suresh", "Suresh", "D", "Financial Time Series", "financial time series, stochastic processes and insurance."),
    # ---------------- IIM Lucknow
    ("IIM L", "Alok Dixit", "Dixit", "D", "Derivatives Pricing and Market Efficiency", "derivatives pricing and market efficiency, and on quantitative trading strategies."),
    ("IIM L", "Asim Kumar Mishra", "Mishra", "A", "Investment Banking and Venture Capital Financing", "investment banking, venture capital financing and corporate finance."),
    ("IIM L", "Madhumita Chakraborty", "Chakraborty", "A", "Market Efficiency and Asset Pricing", "market efficiency, market anomalies and asset pricing, and on behavioral finance."),
    ("IIM L", "Sowmya Subramaniam", "Subramaniam", "A", "Bond Markets and Credit Default Swaps", "sovereign and corporate bond markets, credit default swaps and cryptocurrencies."),
    ("IIM L", "Madhusudan Karmakar", "Karmakar", "D", "Portfolio Risk Management", "portfolio risk management based on GARCH-EVT-Copula models and copula-based hedging strategies."),
    ("IIM L", "Prakash Singh", "Singh", "A", "Bank Regulation and Risk Management", "Basel III adoption, bank regulation and risk management in banks and financial institutions."),
    ("IIM L", "Ranjan Kumar", "Kumar", "A", "Sustainability and ESG Communication", "sustainability and ESG communication, and strategic and financial communication."),
    ("IIM L", "Ashish Pandey", "Pandey", "A", "Financial Intermediation and Financial Institutions", "financial intermediation and financial institutions, and capital market research in accounting."),
    ("IIM L", "Kaushik Bhattacharya", "Bhattacharya", "B", "Monetary Policy and Central Banking", "applied econometrics and time series analysis, and monetary policy and central banking."),
    ("IIM L", "Himadri Shekhar Chakrabarty", "Chakrabarty", "B", "Public Finance and Banking", "public finance and banking, and applied macroeconomics."),
    ("IIM L", "Kushankur Dey", "Dey", "A", "Sustainability and Green Financing", "sustainability and green financing, and blockchain and IoT for sustainable e-agriculture."),
    ("IIM L", "Mrityunjay Kumar Tiwary", "Tiwary", "A", "Banking and Financial Markets", "banking, financial markets and accounting."),
    ("IIM L", "Krishna Chandra Balodi", "Balodi", "C", "Entrepreneurial Ecosystems", "entrepreneurial ecosystems, digital platform business models and growth strategies for MSMEs."),
    ("IIM L", "Yash Daultani", "Daultani", "D", "Supply Chain Analytics", "supply chain analytics, digital transformation and multi-criteria decision-making."),
    ("IIM L", "Dhirendra Mani Shukla", "Shukla", "C", "Strategic Alliances and Innovation", "strategic alliances, social entrepreneurship and innovation."),
    # ---------------- IIM Mumbai
    ("IIM Mumbai", "M. Venkateswarlu", "Venkateswarlu", "D", "Financial Economics and Corporate Finance", "financial economics, corporate finance and capital structure, and financial forecasting."),
    ("IIM Mumbai", "Ruchita Gupta", "Gupta", "D", "Product and Technology Forecasting", "product and technology forecasting, and technology entrepreneurship."),
    ("IIM Mumbai", "Ajaya Kumar Panda", "Panda", "A", "Dynamic Capital Structure", "dynamic capital structure and the transmission of monetary policy stimulus to firm profitability."),
    ("IIM Mumbai", "Rakesh D. Raut", "Raut", "D", "Digital Strategy and Supply Chain Risk Management", "digital strategy and transformation, supply chain risk management and multi-criteria decision making."),
    ("IIM Mumbai", "Binilkumar Amarayil Sreeraman", "Binilkumar", "B", "Energy Transition", "energy transition and energy poverty, and sustainable mobility."),
    ("IIM Mumbai", "Hema Diwan", "Diwan", "A", "ESG and Non-Financial Reporting", "ESG and non-financial reporting, and the circular economy."),
    ("IIM Mumbai", "Poonam Singh", "Singh", "B", "Competition Policy and Corporate Governance", "competition policy, corporate governance and public policy."),
    ("IIM Mumbai", "Utpal Chattopadhyay", "Chattopadhyay", "C", "Competitiveness and Inclusive Growth", "competitiveness, inclusive growth and strategic alliances."),
    ("IIM Mumbai", "Hema Date", "Date", "D", "Artificial Intelligence and Business Analytics", "artificial intelligence and machine learning, business intelligence and data analytics, and supply chain management."),
    ("IIM Mumbai", "Rony Mitra", "Mitra", "D", "Data Analytics and Supply Chain Finance", "data analytics, supply chain finance and machine learning."),
    ("IIM Mumbai", "Debabrata Das", "Das", "D", "Optimization and Business Analytics", "optimization techniques, business analytics and machine learning."),
    ("IIM Mumbai", "Neeraj Pandey", "Pandey", "E", "Pricing and Revenue Management", "pricing and revenue management, consumer analytics and advanced AI applications in marketing."),
    ("IIM Mumbai", "Sanjeev Verma", "Verma", "E", "Artificial Intelligence in Marketing", "artificial intelligence in marketing and marketing analytics."),
    ("IIM Mumbai", "Disha Sharma", "Sharma", "A", "Climate Policy and Green Growth", "climate science and policy, emission trading and green growth."),
    ("IIM Mumbai", "Priyanka Verma", "Verma", "D", "Supply Chain Modeling and Analytics", "optimization, supply chain modeling and supply chain analytics."),
]
CHECK_SURNAME = {"Binilkumar Amarayil Sreeraman", "Saravana Jaikumar L.", "Jijo Lukose P J"}


def main():
    short = {(r["institute"], r["name"]): r for r in csv.DictReader((D / "shortlist.csv").open(encoding="utf-8-sig"))}
    dnc = {r["profile_url"] for r in csv.DictReader((D / "do_not_contact.csv").open(encoding="utf-8-sig"))}
    rows, review, seen = [], ["# Batch 1 review: 15 per IIM (draft)\n",
                              "Check each line against the official research text under it. Change anything in data/batch.csv.\n"], set()
    for inst, name, surname, field, topic, rest in PICKS:
        s = short.get((inst, name))
        if not s:
            raise SystemExit(f"not on the official shortlist: {inst} {name}")
        if s["profile_url"] in dnc or s["email"] in seen:
            raise SystemExit(f"excluded or duplicate: {inst} {name}")
        seen.add(s["email"])
        line = F + rest
        rows.append({"name": name, "surname": surname, "institute": inst, "email": s["email"], "field": field,
                     "subject_topic": topic, "opening_line": line, "profile_url": s["profile_url"], "status": "draft"})
        if not review[-1].startswith(f"## {inst}") and all(not x.startswith(f"## {inst}") for x in review):
            review.append(f"\n## {inst}\n")
        flag = "  **(check: how to address this professor)**" if name in CHECK_SURNAME else ""
        review.append(f"**{name}** <{s['email']}> · Dear Professor {surname}{flag} · paragraph {field}\n"
                      f"Subject: Interest in Research on {topic}\n> {line}\n\nOfficial text: {s['research_text'][:300]}\n")
    cols = ["name", "surname", "institute", "email", "field", "subject_topic", "opening_line", "profile_url",
            "status", "sent_at", "message_id"]
    with (D / "batch.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (ROOT / "batch_review.md").write_text("\n".join(review), encoding="utf-8")
    from collections import Counter
    print(len(rows), "drafts", dict(Counter(r["institute"] for r in rows)))


if __name__ == "__main__":
    main()
