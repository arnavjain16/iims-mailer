"""
Shared helpers for the professor-list scripts (Phase 1).

What this file does, in plain words:
  * fetch(url)   downloads a web page politely and SAVES it in the cache/ folder,
                 so the same page is never downloaded twice.
  * It waits a couple of seconds between real downloads.
  * It introduces itself with a clear User-Agent.
  * It checks the site's robots.txt first and refuses to fetch a page the site
    asks robots not to fetch.
Nothing here guesses or invents data. It only downloads and saves pages.
"""
import hashlib
import json
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import requests

PROJECT = Path(__file__).resolve().parent.parent
CACHE = PROJECT / "cache"
CACHE.mkdir(exist_ok=True)

# A clear, honest name for this reader. No personal contact details are sent.
USER_AGENT = "IITB-student-faculty-page-reader/0.1 (reads public faculty pages, a few at a time)"
DELAY_SECONDS = 5.0           # pause between real (non-cached) downloads
_last_request_time = 0.0
_robots = {}                  # one robots.txt parser per website


def _robots_allows(url):
    """True if the site's robots.txt allows us to fetch this url."""
    parts = urlparse(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            resp = requests.get(base + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.parse([])          # no robots.txt (or unreadable) means nothing is disallowed
        except requests.RequestException:
            rp.parse([])
        _robots[base] = rp
    return _robots[base].can_fetch(USER_AGENT, url)


def fetch(url):
    """
    Return a dict: {"url", "status", "text", "from_cache", "blocked_by_robots"}.
    Pages are cached by URL, so a second call costs nothing and sends no request.
    """
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()
    meta_file = CACHE / f"{key}.json"
    body_file = CACHE / f"{key}.html"
    if meta_file.exists() and body_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        meta["text"] = body_file.read_text(encoding="utf-8", errors="replace")
        meta["from_cache"] = True
        return meta

    if not _robots_allows(url):
        return {"url": url, "status": None, "text": "", "from_cache": False, "blocked_by_robots": True}

    global _last_request_time
    wait = DELAY_SECONDS - (time.time() - _last_request_time)
    if wait > 0:
        time.sleep(wait)
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        status, text = resp.status_code, resp.text
        final_url = resp.url
    except requests.RequestException as exc:
        status, text, final_url = None, f"ERROR: {exc}", url
    _last_request_time = time.time()

    meta = {"url": url, "final_url": final_url, "status": status,
            "blocked_by_robots": False, "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if status is not None and status < 500:          # never cache network errors / server errors
        body_file.write_text(text, encoding="utf-8")
        meta_file.write_text(json.dumps(meta, indent=1), encoding="utf-8")
    meta["text"] = text
    meta["from_cache"] = False
    return meta
