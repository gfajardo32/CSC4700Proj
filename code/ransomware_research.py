import requests
import time
import csv
import re
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Optional, Union, List, Dict

BASE_URL  = "https://api.ransomware.live/v2"
GROUPS    = ["qilin", "thegentlemen", "akira", "incransom", "play"]

MANUFACTURING_KEYWORDS = [
    "manufactur", "industrial", "automotive", "aerospace", "chemical",
    "textile", "assembly", "factory", "fabricat", "machiner", "equipment",
    "plastics", "rubber", "steel", "metal", "aluminum", "packaging",
    "semiconductor", "electronics manufactur", "food processing",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}
REQUEST_DELAY = 1.2
NEWS_LIMIT    = 3


def safe_get(url: str, retries: int = 3) -> Optional[Union[dict, list]]:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  rate limited, waiting {wait}s")
                time.sleep(wait)
            elif resp.status_code == 404:
                print(f"  404: {url}")
                return None
            else:
                print(f"  HTTP {resp.status_code}: {url}")
                return None
        except requests.RequestException as e:
            print(f"  request error ({e}): {url}")
            time.sleep(5)
    return None


def is_manufacturing(victim: dict) -> bool:
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
        print(f"  news search error for '{company_name}': {e}")
    return results


def write_csv(path: str, rows: List[Dict], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  saved: {path} ({len(rows)} rows)")


# step 1 - fetch all victims per group

print("step 1: fetching victims for each group")

all_victims: List[Dict] = []
victims_by_group: Dict[str, list] = {}

for group in GROUPS:
    url  = f"{BASE_URL}/groupvictims/{group}"
    print(f"  {group}: {url}")
    data = safe_get(url)
    time.sleep(REQUEST_DELAY)

    if not data:
        print(f"  no data returned for {group}")
        victims_by_group[group] = []
        continue

    victims = data if isinstance(data, list) else data.get("victims", [])
    victims_by_group[group] = victims
    print(f"  {len(victims)} victims retrieved")

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

print(f"  total victims across all groups: {len(all_victims)}")


# step 2 - filter manufacturing sector

print("\nstep 2: filtering manufacturing sector victims")

manufacturing_victims: List[Dict] = []
for v in all_victims:
    if is_manufacturing(v):
        manufacturing_victims.append(v)

print(f"  manufacturing victims found: {len(manufacturing_victims)}")
for v in manufacturing_victims[:10]:
    print(f"  [{v['group']}] {v['victim']} ({v['country']}) - {v['activity'] or v['sector']}")


# step 3 - news search for top manufacturing victims

print("\nstep 3: news search for top manufacturing victims")

seen_names = set()
top_mfg: List[Dict] = []
for v in manufacturing_victims:
    name = v["victim"].strip()
    if name and name not in seen_names:
        seen_names.add(name)
        top_mfg.append(v)
    if len(top_mfg) >= 5:
        break

news_rows: List[Dict] = []
for v in top_mfg:
    print(f"  searching: {v['victim']} ({v['group']})")
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
        print(f"    {len(articles)} article(s) found")
    else:
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
        print(f"    {len(articles2)} article(s) found (broad search)")


# step 4 - victim overlap across groups

print("\nstep 4: victim overlap analysis")

victim_to_groups: Dict[str, set] = defaultdict(set)
for v in all_victims:
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
print(f"  victims claimed by 2+ groups: {len(overlap_rows)}")
for r in overlap_rows[:10]:
    print(f"  {r['victim_normalised']} -> {r['groups']}")


# step 5 - write CSVs

print("\nstep 5: writing CSV files")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "CSVs")
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

print("\ndone. files saved to:", OUTPUT_DIR)
