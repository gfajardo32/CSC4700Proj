import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

GROUPS = ["qilin", "thegentlemen", "akira", "incransom", "play"]
BASE_URL = "https://www.ransomware.live/group/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_group(group_name):
    url = BASE_URL + group_name
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"  Failed to fetch {group_name}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Total number of victims
    total_victims = " "
    for tag in soup.find_all(string=True):
        if "Victims" in tag:
            parent = tag.find_parent()
            if parent:
                next_sibling = parent.find_next_sibling()
                if next_sibling and next_sibling.get_text(strip=True).isdigit():
                    total_victims = int(next_sibling.get_text(strip=True))
                    break

    # Top 5 Sectors
    sectors = []
    sector_header = soup.find(string=lambda t: t and "Top 5 Activity Sectors" in t)
    if sector_header:
        container = sector_header.find_parent()
        items = container.find_next_sibling("ul") or container.find_parent().find("ul")
        if items:
            for li in items.find_all("li")[:5]:
                text = li.get_text(separator=" ", strip=True)
                sectors.append(text)

    # Top 5 Countries
    countries = []
    country_header = soup.find(string=lambda t: t and "Top 5 Countries" in t)
    if country_header:
        container = country_header.find_parent()
        items = container.find_next_sibling("ul") or container.find_parent().find("ul")
        if items:
            for li in items.find_all("li")[:5]:
                text = li.get_text(separator=" ", strip=True)
                countries.append(text)

    # Results
    top_5_sectors = ", ".join(sectors) if sectors else "N/A"
    primary_sector = sectors[0] if sectors else "N/A"
    top_5_countries = ", ".join(countries) if countries else "N/A"
    primary_country = countries[0] if countries else "N/A"

    return {
        "group_name": group_name,
        "total_victims": total_victims,
        "top_5_sectors": top_5_sectors,
        "primary_sector": primary_sector,
        "top_5_countries": top_5_countries,
        "primary_country": primary_country
    }

# Run
results = []
for group in GROUPS:
    print(f"Scraping: {group}")
    data = scrape_group(group)
    if data:
        results.append(data)
        print(f"  Victims: {data['total_victims']}")
        print(f"  Primary sector: {data['primary_sector']}")
        print(f"  Primary country: {data['primary_country']}")
    time.sleep(2)  # small buffer between requests

df = pd.DataFrame(results)
print("\n--- Summary ---")
print(df.to_string(index=False))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "CSVs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, "group_summary.csv")
df.to_csv(output_path, index=False)
print("\nSaved to", output_path)
