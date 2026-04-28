import requests
import json
import time
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

GROUPS = ["qilin", "thegentlemen", "akira", "incransom", "play"]

for group in GROUPS:
    print(f"Fetching data for: {group}")

    response = requests.get(f"https://api.ransomware.live/v2/group/{group}", headers=HEADERS)

    if response.status_code == 200:
        data = response.json()

        filename = os.path.join(OUTPUT_DIR, f"{group}_group.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"  Saved to {filename}")
    else:
        print(f"  Failed: {response.status_code}")

    time.sleep(2)