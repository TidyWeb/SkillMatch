"""Self-check: render /results and three /job pages for every persona, in fixtures and live mode.

Flags mechanical problems (the literal word None, nan, raw HTML in text, error text, empty lists,
broken internal links, identical results across personas) and writes the visible text of every
page to reports/self_check/ for a human read.

Usage: uv run python scripts/self_check.py [--live-db data/processed/skillmatch.db]
"""

import argparse
import json
import re
import tempfile
from html.parser import HTMLParser
from pathlib import Path

from skillmatch import config
from skillmatch.etl.pipeline import run
from skillmatch.profile import personas
from skillmatch.web import create_app


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template", "datalist"):
            self.skip += 1
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "tr", "dt", "dd", "summary", "div", "br"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template", "datalist"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    @property
    def text(self):
        return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t]+", " ", "".join(self.parts))).strip()


PROBLEMS = [
    (re.compile(r"\bNone\b"), "the word None"),
    (re.compile(r"\bnan\b", re.I), "nan"),
    (re.compile(r"<[a-z]+[ >/]|&lt;|&gt;|&amp;amp;"), "raw HTML in text"),
    (re.compile(r"Traceback|Internal Server Error|undefined|jinja", re.I), "error text"),
    (re.compile(r"\{\w+\}"), "unfilled placeholder"),
    (re.compile(r"\bas a a\b|\ban an\b|\ba an\b|\.\.(?!\.)"), "grammar slip"),
]
EMPTY = re.compile(r"<(ul|ol|dl|tbody)[^>]*>\s*</\1>")


def check_page(client, path, html, out_dir, name, issues, checked_links):
    t = Text()
    t.feed(html)
    text = t.text
    (out_dir / f"{name}.txt").write_text(text)
    for pat, what in PROBLEMS:
        for m in pat.finditer(text):
            ctx = text[max(0, m.start() - 60) : m.end() + 60].replace("\n", " ")
            issues.append(f"{name}: {what}: …{ctx}…")
    if EMPTY.search(html):
        issues.append(f"{name}: empty list or table")
    for href in t.links:
        if href.startswith("/") and href not in checked_links:
            checked_links.add(href)
            if client.get(href).status_code != 200:
                issues.append(f"{name}: broken internal link {href}")
        elif href.startswith("http://"):
            issues.append(f"{name}: insecure link {href}")
        elif not href.startswith(("https://", "/", "#")):
            issues.append(f"{name}: odd link {href!r}")
    return text


def check_mode(label, db, out_root):
    out_dir = out_root / label
    out_dir.mkdir(parents=True, exist_ok=True)
    client = create_app({"TESTING": True, "DB_PATH": str(db)}).test_client()
    issues, signatures, checked = [], {}, set()
    for page in ["/", "/results", "/insights", "/sources", "/about"]:
        r = client.get(page)
        if r.status_code != 200:
            issues.append(f"GET {page}: {r.status_code}")
        check_page(
            client, page, r.data.decode(), out_dir, "page" + page.replace("/", "_"), issues, checked
        )
    for pid, data in personas().items():
        prof = json.dumps(data)
        r = client.post("/results", data={"profile": prof})
        html = r.data.decode()
        text = check_page(client, "/results", html, out_dir, f"{pid}_results", issues, checked)
        ids = re.findall(r'href="/job/([^"]+)"', html)
        ids = list(dict.fromkeys(ids))
        signatures[pid] = tuple(ids[:15])
        if "How your background answers this" not in text:
            issues.append(f"{pid}: no 'answers this' lines on results")
        for job_id in ids[:3]:
            g = client.get(f"/job/{job_id}")
            p = client.post(f"/job/{job_id}", data={"profile": prof})
            if g.status_code != 200 or p.status_code != 200:
                issues.append(f"{pid}: job {job_id} returned {g.status_code}/{p.status_code}")
            safe = job_id.replace(":", "_")
            check_page(
                client,
                f"/job/{job_id}",
                g.data.decode(),
                out_dir,
                f"{pid}_job_{safe}_page",
                issues,
                checked,
            )
            check_page(
                client,
                f"/job/{job_id}",
                p.data.decode(),
                out_dir,
                f"{pid}_job_{safe}_coverage",
                issues,
                checked,
            )
        r = client.post("/insights", data={"profile": prof})
        check_page(
            client, "/insights", r.data.decode(), out_dir, f"{pid}_insights", issues, checked
        )
    if len(set(signatures.values())) < len(signatures):
        issues.append(f"{label}: some personas got identical top-15 result lists")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-db", default=str(config.DB_PATH))
    args = ap.parse_args()
    out_root = config.REPORTS_DIR / "self_check"
    with tempfile.TemporaryDirectory() as tmp:
        fx = Path(tmp) / "fixtures.db"
        run("fixtures", db_path=fx, reports_dir=Path(tmp), offline=True)
        results = {"fixtures": check_mode("fixtures", fx, out_root)}
    live = Path(args.live_db)
    if live.exists():
        results["live"] = check_mode("live", live, out_root)
    for label, issues in results.items():
        print(f"== {label}: {len(issues)} issue(s)")
        for i in issues[:200]:
            print("  -", i)
    print(f"page text written to {out_root}")


if __name__ == "__main__":
    main()
