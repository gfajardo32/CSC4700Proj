"""
ransomware_research.py
======================
Pulls data from the ransomware.live API v2 for 5 threat groups:
  Qilin, TheGentleMan, Akira, Incransom, Play

What this script does:
  1. Fetches all victims claimed by each group
  2. Filters for Manufacturing sector victims
  3. Picks up to 5 manufacturing victims and searches Google News RSS
     for real-world impact (financial loss, downtime, public statements)
  4. Checks for victim overlap — same org hit by multiple groups
  5. Saves everything to CSV files:
       - all_victims.csv          → every victim across all 5 groups
       - manufacturing_victims.csv → manufacturing-only subset
       - news_hits.csv             → news article results per company
       - victim_overlap.csv        → companies hit by 2+ groups
"""

import requests
import time
import csv
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Optional, Union, List, Dict

# ── Configuration ────────────────────────────────────────────────────────────
BASE_URL  = "https://api.ransomware.live/v2"
GROUPS    = ["qilin", "thegentleman", "akira", "incransom", "play"]

# Keywords that suggest a victim belongs to the Manufacturing sector.
# The API doesn't always return a clean "sector" field, so we use the
# activityTags / activity field when available, plus a keyword fallback.
MANUFACTURING_KEYWORDS = [
    "manufactur", "industrial", "automotive", "aerospace", "chemical",
    "textile", "assembly", "factory", "fabricat", "machiner", "equipment",
    "plastics", "rubber", "steel", "metal", "aluminum", "packaging",
    "semiconductor", "electronics manufactur", "food processing",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (research-script)"}
REQUEST_DELAY = 1.2   # seconds between API calls to stay under rate limit
NEWS_LIMIT    = 3     # max news articles to fetch per company

# ── Helpers ──────────────────────────────────────────────────────────────────

def safe_get(url: str, retries: int = 3) -> Optional[Union[dict, list]]:
    """GET with retries and polite delay."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  ⚠ Rate limited. Waiting {wait}s …")
                time.sleep(wait)
            elif resp.status_code == 404:
                print(f"  ✗ 404 Not Found: {url}")
                return None
            else:
                print(f"  ✗ HTTP {resp.status_code}: {url}")
                return None
        except requests.RequestException as e:
            print(f"  ✗ Request error ({e}): {url}")
            time.sleep(5)
    return None


def is_manufacturing(victim: dict) -> bool:
    """Return True if the victim record looks like a manufacturing org."""
    # Fields that may carry sector / activity info
    fields_to_check = [
        str(victim.get("activity", "")),
        str(victim.get("activityTags", "")),
        str(victim.get("sector", "")),
        str(victim.get("description", "")),
        str(victim.get("tags", "")),
    ]
    haystack = " ".join(fields_to_check).lower()
    return any(kw in haystack for kw in MANUFACTURING_KEYWORDS)


def search_news(company_name: str, group_name: str, max_results: int = NEWS_LIMIT) -> List[Dict]:
    """
    Query Google News RSS for news about a ransomware attack on the company.
    Returns a list of {title, link, published} dicts.
    """
    query = f'"{company_name}" ransomware {group_name}'
    encoded = requests.utils.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    results  = []
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return results
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            return results
        for item in channel.findall("item")[:max_results]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link",  "").strip()
            pub   = item.findtext("pubDate", "").strip()
            results.append({"title": title, "link": link, "published": pub})
    except Exception as e:
        print(f"  ⚠ News search error for '{company_name}': {e}")
    return results


# ── Step 1 — Fetch all victims per group ─────────────────────────────────────

print("=" * 60)
print("Step 1 — Fetching victims for each group")
print("=" * 60)

all_victims: List[Dict] = []       # flat list, one row per victim
victims_by_group: Dict[str, list]  = {}

for group in GROUPS:
    url  = f"{BASE_URL}/groupvictims/{group}"
    print(f"\n→ {group}: {url}")
    data = safe_get(url)
    time.sleep(REQUEST_DELAY)

    if not data:
        print(f"  No data returned for {group}.")
        victims_by_group[group] = []
        continue

    # The endpoint returns a list of victim dicts
    victims = data if isinstance(data, list) else data.get("victims", [])
    victims_by_group[group] = victims
    print(f"  ✓ {len(victims)} victims retrieved")

    for v in victims:
        row = {
            "group":       group,
            "victim":      v.get("victim",      v.get("name", "")),
            "attackdate":  v.get("attackdate",  v.get("date", "")),
            "country":     v.get("country",     ""),
            "activity":    v.get("activity",    v.get("activityTags", "")),
            "sector":      v.get("sector",      ""),
            "website":     v.get("website",     ""),
            "description": str(v.get("description", ""))[:300],
        }
        all_victims.append(row)

print(f"\n✓ Total victims across all groups: {len(all_victims)}")


# ── Step 2 — Filter Manufacturing ────────────────────────────────────────────

print("\n" + "=" * 60)
print("Step 2 — Filtering Manufacturing sector victims")
print("=" * 60)

manufacturing_victims: List[Dict] = []
for v in all_victims:
    # Build a combined dict that includes original raw fields for is_manufacturing()
    # We stored activity + sector already; re-check against those
    if is_manufacturing(v):
        manufacturing_victims.append(v)

print(f"✓ Manufacturing victims found: {len(manufacturing_victims)}")
for v in manufacturing_victims[:10]:
    print(f"  • [{v['group']}] {v['victim']} ({v['country']}) — {v['activity'] or v['sector']}")


# ── Step 3 — Pick 3–5 companies & search news ────────────────────────────────

print("\n" + "=" * 60)
print("Step 3 — News search for top manufacturing victims")
print("=" * 60)

# Deduplicate by victim name, pick up to 5
seen_names = set()
top_mfg: List[Dict]  = []
for v in manufacturing_victims:
    name = v["victim"].strip()
    if name and name not in seen_names:
        seen_names.add(name)
        top_mfg.append(v)
    if len(top_mfg) >= 5:
        break

news_rows: List[Dict] = []
for v in top_mfg:
    print(f"\n  Searching news: {v['victim']} ({v['group']})")
    articles = search_news(v["victim"], v["group"])
    time.sleep(REQUEST_DELAY)
    if articles:
        for art in articles:
            news_rows.append({
                "victim":      v["victim"],
                "group":       v["group"],
                "attackdate":  v["attackdate"],
                "country":     v["country"],
                "news_title":  art["title"],
                "news_link":   art["link"],
                "news_date":   art["published"],
            })
        print(f"    ✓ {len(articles)} article(s) found")
    else:
        # If no group-specific results, try a broader query
        articles2 = search_news(v["victim"], "ransomware attack")
        time.sleep(REQUEST_DELAY)
        for art in articles2:
            news_rows.append({
                "victim":      v["victim"],
                "group":       v["group"],
                "attackdate":  v["attackdate"],
                "country":     v["country"],
                "news_title":  art["title"],
                "news_link":   art["link"],
                "news_date":   art["published"],
            })
        print(f"    ✓ {len(articles2)} article(s) found (broad search)")


# ── Step 4 — Victim overlap across groups ─────────────────────────────────────

print("\n" + "=" * 60)
print("Step 4 — Victim overlap analysis")
print("=" * 60)

# Map normalised victim name → set of groups that claimed them
victim_to_groups: Dict[str, set] = defaultdict(set)
for v in all_victims:
    # Normalise: lowercase, strip whitespace, collapse spaces
    name = re.sub(r"\s+", " ", v["victim"].strip().lower())
    if name:
        victim_to_groups[name].add(v["group"])

overlap_rows: List[Dict] = []
for name, grps in sorted(victim_to_groups.items()):
    if len(grps) > 1:
        overlap_rows.append({
            "victim_normalised": name,
            "groups":            ", ".join(sorted(grps)),
            "group_count":       len(grps),
        })

overlap_rows.sort(key=lambda r: -r["group_count"])
print(f"✓ Victims claimed by 2+ groups: {len(overlap_rows)}")
for r in overlap_rows[:10]:
    print(f"  • {r['victim_normalised']}  →  {r['groups']}")


# ── Step 5 — Write CSVs ───────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Step 5 — Writing CSV files")
print("=" * 60)

def write_csv(path: str, rows: List[Dict], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {path}  ({len(rows)} rows)")

import os
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSVs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

write_csv(
    f"{OUTPUT_DIR}/all_victims.csv",
    all_victims,
    ["group", "victim", "attackdate", "country", "activity", "sector", "website", "description"],
)

write_csv(
    f"{OUTPUT_DIR}/manufacturing_victims.csv",
    manufacturing_victims,
    ["group", "victim", "attackdate", "country", "activity", "sector", "website", "description"],
)

write_csv(
    f"{OUTPUT_DIR}/news_hits.csv",
    news_rows,
    ["victim", "group", "attackdate", "country", "news_title", "news_link", "news_date"],
)

write_csv(
    f"{OUTPUT_DIR}/victim_overlap.csv",
    overlap_rows,
    ["victim_normalised", "groups", "group_count"],
)

print("\n✅ All done! Files saved to:", OUTPUT_DIR)
print("""
Output files (inside CSVs/):
  all_victims.csv          — every victim across Qilin, TheGentleMan, Akira, Incransom, Play
  manufacturing_victims.csv — manufacturing-sector subset
  news_hits.csv             — Google News articles per manufacturing company
  victim_overlap.csv        — companies targeted by 2+ groups
""")