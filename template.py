"""
Startup internship email: one short template, four project paragraphs chosen by track.
Every fact about Arnav comes from resume.pdf. {company} and {what} come from the database.
"""

SUBJECTS = {
    "vc": "Investment Analyst Internship | IIT Bombay undergraduate",
    "finance": "Internship: Finance / Strategy / Founder's Office | IIT Bombay undergraduate",
    "fintech": "Internship: Strategy / Founder's Office / Finance | IIT Bombay undergraduate",
    "consumer": "Internship: Founder's Office / Strategy / Growth | IIT Bombay undergraduate",
    "tech": "Internship: Strategy / BizOps / Product | IIT Bombay undergraduate",
}

ROLES = {
    "vc": "an investment analyst intern",
    "finance": "an intern in finance, strategy or the founder's office",
    "fintech": "an intern in strategy, finance or the founder's office",
    "consumer": "an intern in the founder's office, strategy or growth",
    "tech": "an intern in strategy, business operations or product",
}

PROJECTS = {
    "vc": (
        "Most of my work so far is in valuation and research. I wrote a 37-page Buy-rated equity research "
        "report on SPR Auto Technologies (CAPM-WACC DCF and DuPont analysis) that reached the final top 10 at "
        "IIT Bombay's Finance Club, built a 10-year DCF with peer comparables for Varun Beverages, and am "
        "building a venue investment and IRR framework for PlayAll Sports. I also researched UPI's business "
        "model and India's CBDC (top 10 of 300+ teams)."
    ),
    "finance": (
        "Most of my work so far is in finance. I wrote a 37-page equity research report with a CAPM-WACC DCF "
        "that reached the final top 10 at IIT Bombay's Finance Club, built a 10-year DCF with peer comparables "
        "for Varun Beverages, and am building a venue investment and IRR framework for PlayAll Sports. I also "
        "researched UPI's business model and India's CBDC (top 10 of 300+ teams)."
    ),
    "fintech": (
        "I researched UPI's business model and the rise of India's CBDC (top 10 of 300+ teams), mapping the "
        "revenue models of four UPI intermediaries. I also wrote a 37-page equity research report with a "
        "CAPM-WACC DCF that reached the final top 10 at IIT Bombay's Finance Club, and am building a venue "
        "investment and IRR framework for PlayAll Sports."
    ),
    "consumer": (
        "I am an Associate Consultant in IIT Bombay's Consulting Core Group, where I co-wrote a casebook of 38 "
        "real cases and led a product teardown of Strava. I am also building a data-driven venue investment and "
        "IRR framework for PlayAll Sports, and wrote a 37-page equity research report that reached the final "
        "top 10 at IIT Bombay's Finance Club."
    ),
    "tech": (
        "I am an Associate Consultant in IIT Bombay's Consulting Core Group, where I co-launched an 80-page "
        "Product Management guide and led a product teardown of Strava. I am also building a data-driven venue "
        "investment and IRR framework (40+ variables) for PlayAll Sports, and work in Python (pandas, NumPy) "
        "and Excel."
    ),
}

BODY = """Dear {company} team,

I am Arnav Jain, an undergraduate at IIT Bombay (CPI 9.13) pursuing a Minor in Artificial Intelligence and Data Science. I am writing to ask whether {company} has room for {role}; I would be glad to contribute to its work on {what}.

{projects}

I am available for a winter internship from December 2026 to January 2027, {where}, and can continue part-time after that. I am eager to learn and happy to take on whatever work is most useful to the team.

My resume is attached for your review. Thank you for your time and consideration.

Sincerely,
Arnav Jain
B.S., Centre for Multidisciplinary Education, Minor in Artificial Intelligence and Data Science
Indian Institute of Technology Bombay
M: +91 8169991371 | arnavj3061@gmail.com
"""

FOLLOWUP = """Dear {company} team,

I am following up on my email below about {role_short}internship opportunities at {company}. I would be glad to share anything else that helps, and my resume is attached again for convenience.

Thank you for your time.

Sincerely,
Arnav Jain
IIT Bombay | +91 8169991371
"""


def render(company, track, what, city="Mumbai"):
    track = track if track in PROJECTS else "consumer"
    subject = SUBJECTS[track]
    where = "on-site in Mumbai or remotely" if city == "Mumbai" else "remotely or on-site"
    body = BODY.format(company=company, role=ROLES[track], what=what, projects=PROJECTS[track], where=where)
    return subject, body
