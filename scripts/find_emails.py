"""
Builds the startup database.

For every company in seed_companies.csv it reads the company's OWN website
(home page plus careers / jobs / contact / about pages linked from it) and
records every email address printed there, with the page it came from.

Nothing is guessed: an address goes into the database only if it is printed
on the company's own site. Addresses are sorted into:
  hiring  - careers@, jobs@, hr@, talent@, hiring@, people@ ...
  general - hello@, contact@, info@, team@, founders@ ...
  other   - everything else (support, grievance, sales, personal names ...);
            stored but never picked automatically.

Output: startups.db (SQLite) and startups.xlsx (for viewing).
Run:    python scripts/find_emails.py            (all companies)
        python scripts/find_emails.py --only Jupiter,Dhan
"""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
import threading
import time
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
CACHE.mkdir(exist_ok=True)
DB_PATH = ROOT / "startups.db"
SEED = ROOT / "seed_companies.csv"

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 student-careers-page-reader")
PAGE_LIMIT = 9
PAUSE = 1.0

LINK_WORDS = ("career", "job", "join", "hiring", "work-with", "workwith", "life-at", "lifeat",
              "contact", "about", "team", "people", "culture", "intern")
GUESS_PATHS = ("/careers", "/career", "/jobs", "/contact", "/contact-us", "/about", "/about-us", "/join-us")
ATS_HOSTS = ("lever.co", "greenhouse.io", "ashbyhq.com", "keka.com", "darwinbox", "zohorecruit",
             "freshteam", "workable.com", "wellfound.com", "notion.site", "instahyre.com",
             "cutshort.io", "kekahire", "hirist", "recruitee", "smartrecruiters", "breezy.hr",
             "springrecruit", "superset", "linkedin.com/company")

HIRING = ("careers", "career", "jobs", "job", "hiring", "hire", "talent", "recruit", "recruitment",
          "recruiting", "hr", "humanresources", "people", "peopleops", "joinus", "join", "internship",
          "interns", "intern", "work", "workwithus", "ta", "talentacquisition", "resume", "resumes", "cv")
GENERAL = ("hello", "hi", "hey", "contact", "contactus", "info", "team", "connect", "founders",
           "founder", "office", "enquiry", "enquiries", "inquiry", "general", "mail", "namaste", "hola",
           "listen", "talk", "letstalk", "reachus", "reach", "write", "writetous", "sayhello", "hellow", "namaskar")
FREEMAIL = ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com")
JUNK_DOMAINS = ("example.com", "domain.com", "email.com", "sentry.io", "wixpress.com", "sentry-next.wixpress.com",
                "yourdomain.com", "company.com", "mysite.com", "test.com", "users.noreply.github.com")
MUMBAI_WORDS = ("mumbai", "navi mumbai", "thane", "powai", "andheri", "bandra", "lower parel",
                "worli", "goregaon", "malad", "vikhroli", "bkc", "kurla", "santacruz", "prabhadevi")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,10}")
BAD_TAIL = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".js", ".css", ".woff", ".woff2", ".ico")

_robots, _robots_lock = {}, threading.Lock()


def cached_get(url):
    key = hashlib.sha1(url.encode()).hexdigest()
    meta_f, body_f = CACHE / f"{key}.json", CACHE / f"{key}.html"
    if meta_f.exists() and body_f.exists():
        meta = json.loads(meta_f.read_text(encoding="utf-8"))
        meta["text"] = body_f.read_text(encoding="utf-8", errors="replace")
        return meta
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        meta = {"url": url, "final_url": r.url, "status": r.status_code,
                "ctype": r.headers.get("content-type", "")}
        text = r.text if "html" in meta["ctype"] or "text" in meta["ctype"] else ""
    except requests.RequestException as exc:
        meta, text = {"url": url, "final_url": url, "status": None, "error": str(exc)[:200]}, ""
    body_f.write_text(text, encoding="utf-8")
    meta_f.write_text(json.dumps(meta), encoding="utf-8")
    meta["text"] = text
    time.sleep(PAUSE)
    return meta


def robots_ok(url):
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    with _robots_lock:
        rp = _robots.get(base)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(base + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=15)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except requests.RequestException:
            rp.parse([])
        with _robots_lock:
            _robots[base] = rp
    return rp.can_fetch(USER_AGENT, url)


def root_of(host):
    host = host.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "com", "org", "net", "ac", "gov") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def decode_cfemail(hexstr):
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


def extract_emails(html):
    found = set()
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select("a[href^=mailto]"):
        addr = a["href"][7:].split("?")[0].strip()
        found.add(addr)
    for tag in soup.select("[data-cfemail]"):
        found.add(decode_cfemail(tag["data-cfemail"]))
    for a in soup.select("a[href*='/cdn-cgi/l/email-protection#']"):
        found.add(decode_cfemail(a["href"].split("#")[-1]))
    text = html
    text = re.sub(r"\s*[\[\(\{]\s*at\s*[\]\)\}]\s*", "@", text, flags=re.I)
    text = re.sub(r"\s*[\[\(\{]\s*dot\s*[\]\)\}]\s*", ".", text, flags=re.I)
    text = text.replace("&#64;", "@").replace("&#x40;", "@").replace("\\u0040", "@")
    found.update(EMAIL_RE.findall(text))
    clean = set()
    for e in found:
        e = e.strip().strip(".").lower()
        e = re.sub(r"^(u003e|x3e|20|%20)", "", e)
        if not EMAIL_RE.fullmatch(e) or e.endswith(BAD_TAIL):
            continue
        dom = e.split("@")[1]
        if dom in JUNK_DOMAINS or any(dom.endswith(j) for j in JUNK_DOMAINS) or "@2x" in e or "@3x" in e:
            continue
        clean.add(e)
    return clean, soup


def category(email):
    local = re.sub(r"[^a-z]", "", email.split("@")[0].lower())
    raw = email.split("@")[0].lower()
    tokens = set(re.split(r"[._+-]", raw)) | {local}
    if tokens & set(HIRING) or any(local.startswith(w) for w in ("career", "job", "hiring", "talent", "recruit", "intern", "people")):
        return "hiring"
    if tokens & set(GENERAL):
        return "general"
    return "other"


HIRING_ORDER = ("careers", "career", "jobs", "hiring", "talent", "recruit", "intern", "people", "hr")
GENERAL_ORDER = ("founders", "founder", "hello", "team", "hi", "hey", "contact", "info", "connect")


def rank(email):
    local = email.split("@")[0].lower()
    cat = category(email)
    base = {"hiring": 0, "general": 100, "other": 1000}[cat]
    order = HIRING_ORDER if cat == "hiring" else GENERAL_ORDER
    for i, w in enumerate(order):
        if local.startswith(w):
            return base + i
    return base + 50


def process(company):
    domain = company["domain"].strip().lower()
    company_root = root_of(domain)
    result = {"site_ok": 0, "pages": [], "emails": {}, "mumbai": 0, "apply_url": "", "careers_url": "",
              "home_url": "", "note": ""}
    home = None
    for start in (f"https://{domain}/", f"https://www.{domain}/", f"http://{domain}/"):
        if not robots_ok(start):
            result["note"] = "robots.txt disallows"
            continue
        m = cached_get(start)
        if m.get("status") and m["status"] < 400 and m["text"]:
            home = m
            break
    if not home:
        result["note"] = result["note"] or "site not reachable"
        return result
    result["site_ok"] = 1
    result["home_url"] = home["final_url"]
    site_root = root_of(urlparse(home["final_url"]).netloc)
    allowed_roots = {company_root, site_root}

    queue, seen = [home["final_url"]], set()
    pages_html = {home["final_url"]: home["text"]}
    # links from the home page
    soup = BeautifulSoup(home["text"], "html.parser")
    for a in soup.find_all("a", href=True):
        href = urljoin(home["final_url"], a["href"])
        p = urlparse(href)
        label = (a.get_text(" ", strip=True) + " " + href).lower()
        if any(h in href.lower() for h in ATS_HOSTS) and not result["apply_url"]:
            if "linkedin.com" not in href.lower():
                result["apply_url"] = href
        if p.scheme not in ("http", "https") or root_of(p.netloc) not in allowed_roots:
            continue
        if any(w in label for w in LINK_WORDS):
            clean = href.split("#")[0]
            if clean not in queue:
                queue.append(clean)
            if ("career" in label or "job" in label or "join" in label) and not result["careers_url"]:
                result["careers_url"] = clean
    base = f"{urlparse(home['final_url']).scheme}://{urlparse(home['final_url']).netloc}"
    extra_ats = []
    for g in GUESS_PATHS:
        u = base + g
        if u not in queue:
            queue.append(u)

    for url in queue:
        if len(seen) >= PAGE_LIMIT:
            break
        if url in seen:
            continue
        seen.add(url)
        if url in pages_html:
            html = pages_html[url]
        else:
            if not robots_ok(url):
                continue
            m = cached_get(url)
            if not m.get("status") or m["status"] >= 400 or not m["text"]:
                continue
            html = m["text"]
            if not result["careers_url"] and any(w in url.lower() for w in ("career", "job")):
                result["careers_url"] = m["final_url"]
            sp = BeautifulSoup(html, "html.parser")
            for a in sp.find_all("a", href=True):
                href = urljoin(url, a["href"])
                if any(h in href.lower() for h in ATS_HOSTS) and "linkedin.com" not in href.lower() and not result["apply_url"]:
                    result["apply_url"] = href
        result["pages"].append(url)
        emails, sp = extract_emails(html)
        low = sp.get_text(" ", strip=True).lower()
        if any(w in low for w in MUMBAI_WORDS):
            result["mumbai"] = 1
        for e in emails:
            if e not in result["emails"]:
                result["emails"][e] = url
    # the company's own hiring portal (Keka, Lever, Notion ...) can also print a hiring address
    if result["apply_url"] and any(h in result["apply_url"] for h in ("keka.com", "notion.site", "lever.co",
                                                                         "zohorecruit", "darwinbox", "freshteam")):
        if robots_ok(result["apply_url"]):
            m = cached_get(result["apply_url"])
            if m.get("status") and m["status"] < 400 and m["text"]:
                emails, _ = extract_emails(m["text"])
                for e in emails:
                    if root_of(e.split("@")[1]) in allowed_roots and e not in result["emails"]:
                        result["emails"][e] = result["apply_url"]
    return result


def init_db(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE, domain TEXT, city TEXT, sector TEXT, track TEXT, what TEXT,
        site_ok INTEGER, home_url TEXT, mumbai_on_site INTEGER, careers_url TEXT, apply_url TEXT,
        chosen_email TEXT, chosen_category TEXT, chosen_source TEXT,
        status TEXT DEFAULT 'new', sent_at TEXT, message_id TEXT, followup_sent_at TEXT,
        reply TEXT, notes TEXT, scanned_at TEXT);
    CREATE TABLE IF NOT EXISTS emails (
        company_id INTEGER, email TEXT, category TEXT, domain_match INTEGER, source_url TEXT,
        PRIMARY KEY (company_id, email));
    """)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    rows = list(csv.DictReader(SEED.open(encoding="utf-8")))
    if args.only:
        wanted = {x.strip().lower() for x in args.only.split(",")}
        rows = [r for r in rows if r["name"].lower() in wanted]

    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    init_db(con)
    lock = threading.Lock()
    done = [0]

    def work(r):
        try:
            res = process(r)
        except Exception as exc:  # keep going on odd sites
            res = {"site_ok": 0, "pages": [], "emails": {}, "mumbai": 0, "apply_url": "", "careers_url": "",
                   "home_url": "", "note": f"error: {exc}"[:200]}
        company_roots = {root_of(r["domain"]), root_of(urlparse(res["home_url"]).netloc) if res["home_url"] else ""}
        name_token = re.sub(r"[^a-z0-9]", "", r["name"].lower())[:6]
        scored = []
        for e, src in res["emails"].items():
            dom = e.split("@")[1]
            match = int(root_of(dom) in company_roots)
            if dom in FREEMAIL:
                match = 0
            scored.append((e, category(e), match, src))
        pick = sorted([s for s in scored if s[2] and s[1] in ("hiring", "general")], key=lambda s: rank(s[0]))
        chosen = pick[0] if pick else None
        with lock:
            cur = con.execute("SELECT id, status FROM companies WHERE name=?", (r["name"],)).fetchone()
            vals = (r["domain"], r["city"], r["sector"], r["track"], r["what"], res["site_ok"], res["home_url"],
                    res["mumbai"], res["careers_url"], res["apply_url"], time.strftime("%Y-%m-%d %H:%M"), res["note"])
            if cur:
                cid, status = cur
                con.execute("""UPDATE companies SET domain=?, city=?, sector=?, track=?, what=?, site_ok=?, home_url=?,
                               mumbai_on_site=?, careers_url=?, apply_url=?, scanned_at=?, notes=? WHERE id=?""", vals + (cid,))
            else:
                status = "new"
                cid = con.execute("""INSERT INTO companies (domain, city, sector, track, what, site_ok, home_url,
                               mumbai_on_site, careers_url, apply_url, scanned_at, notes, name)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", vals + (r["name"],)).lastrowid
            if status == "new":
                con.execute("UPDATE companies SET chosen_email=?, chosen_category=?, chosen_source=? WHERE id=?",
                            (chosen[0] if chosen else None, chosen[1] if chosen else None,
                             chosen[3] if chosen else None, cid))
            con.execute("DELETE FROM emails WHERE company_id=?", (cid,))
            con.executemany("INSERT OR REPLACE INTO emails VALUES (?,?,?,?,?)",
                            [(cid, e, c, m, s) for e, c, m, s in scored])
            con.commit()
            done[0] += 1
            print(f"[{done[0]}/{len(rows)}] {r['name']}: site={'ok' if res['site_ok'] else 'NO'} "
                  f"emails={len(scored)} chosen={chosen[0] if chosen else '-'}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, rows))
    con.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
