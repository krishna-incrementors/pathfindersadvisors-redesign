"""Refresh src/data/article_keywords.json (topics and grade levels found in each live article).

Usage: python3 tools/index_articles.py   (reads the article list from build.py)
"""
import json, re, sys, html, urllib.request
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if len(sys.argv) > 2:
    out_path, slugs = sys.argv[1], sys.argv[2:]
else:
    _b = (_root / "build.py").read_text()
    _seg = _b[_b.index("ARTICLES = ["):_b.index("CATEGORIES =")]
    slugs = re.findall(r'\("[^"]*?", "([a-z0-9-]+)"', _seg)
    out_path = _root / "src" / "data" / "article_keywords.json"
VOCAB = {
  "freshman": [r"\bfreshm[ae]n\b", r"\b9th\b", r"ninth grade"],
  "sophomore": [r"\bsophomores?\b", r"\b10th\b", r"tenth grade"],
  "junior": [r"\bjuniors?\b(?! college)", r"\b11th\b", r"eleventh grade"],
  "senior": [r"\bseniors?\b(?! year of college)", r"\b12th\b", r"twelfth grade"],
  "FAFSA": [r"\bFAFSA\b"], "CSS Profile": [r"CSS Profile"], "scholarships": [r"scholarship"],
  "merit aid": [r"merit aid|merit scholarship"], "need-based aid": [r"need-based"], "financial aid": [r"financial aid"],
  "529 plan": [r"\b529\b"], "student loans": [r"student loan|private loan|borrow"], "net price": [r"net price"],
  "SAT": [r"\bSAT\b"], "ACT": [r"\bACT\b"], "PSAT": [r"\bPSAT\b"], "National Merit": [r"National Merit"], "AP classes": [r"\bAP\b|Advanced Placement"],
  "test optional": [r"test[- ]optional"], "college essays": [r"\bessays?\b"], "college list": [r"college list"],
  "majors": [r"\bmajors?\b"], "careers": [r"\bcareers?\b"], "AI": [r"\bAI\b|artificial intelligence"],
  "community college": [r"community college"], "trade school": [r"trade school|vocational"], "apprenticeships": [r"apprentice"],
  "military": [r"\bmilitary\b"], "internships": [r"internship"], "co-op": [r"\bco-?ops?\b"],
  "financial advisors": [r"financial (advisor|planner)"], "graduate school": [r"graduate school|law school|med(ical)? school"],
  "ROI": [r"\bROI\b|return on (investment|education)"], "college costs": [r"tuition|cost of (college|attendance)"],
  "admissions": [r"admission"], "four-year graduation": [r"four[- ]year graduation|graduate in four|six[- ]year"],
}
res = {}
for slug in slugs:
    url = f"https://www.pathfindersadvisors.com/{slug}/"
    try:
        import subprocess
        raw = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", url], capture_output=True, timeout=40).stdout.decode("utf-8", "ignore")
    except Exception as ex:
        print("FAIL", slug, ex); res[slug] = []; continue
    i = raw.find("elementor-widget-theme-post-content")
    body = raw[i:] if i != -1 else raw
    # stop at the next Elementor widget after the post body (related posts, footer)
    k = body.find('class="elementor-element ', 10)
    simple = body[:k] if k != -1 else body
    if len(re.sub(r"<[^>]+>", "", simple)) > 1500:
        body = simple
    else:  # post body built from nested Elementor sections: stop at the footer / related posts
        ends = [body.find(m) for m in ("elementor-location-footer", "elementor-widget-posts", "elementor-widget-post-navigation", "<footer")]
        ends = [e for e in ends if e > 0]
        body = body[:min(ends)] if ends else body
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"\s+", " ", text)
    hits = [k for k, pats in VOCAB.items() if any(re.search(p, text, re.I if k not in ("SAT","ACT","PSAT","AI","AP classes","ROI","FAFSA") else 0) for p in pats)]
    res[slug] = hits
    print(f"{len(text):>6} chars  {slug[:60]:<60} {', '.join(hits)}")
json.dump(res, open(out_path, "w"), indent=1)
