#!/usr/bin/env python3
"""
Fetch the configured set of ransomware groups from Ransomware.live API PRO and
build heatmap-ready aggregates (sector / country counts per group).

Groups: akira, play, qilin, thegentlemen, incransom

API: https://api-pro.ransomware.live/docs

Setup:
  cp api_config.example.ini api_config.ini
  # set api_key under [ransomwarelive]

Run:
  python fetch_api_heatmap_data.py

API key: api_config.ini first, else environment variable RANSOMWARELIVE_API_KEY.
Writes output/api_heatmap/heatmap_data.json and heatmap_sector_matrix.csv
"""

from __future__ import annotations

import configparser
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "api_config.ini"
API_BASE_DEFAULT = "https://api-pro.ransomware.live"
API_BASE_ENV = os.environ.get("RANSOMWARELIVE_API_BASE", API_BASE_DEFAULT).rstrip("/")
OUT_DIR = SCRIPT_DIR / "output" / "api_heatmap"
REQUEST_SLEEP_SEC = 0.15

# API group slugs — extend this tuple if you need more groups later.
GROUP_SLUGS: tuple[str, ...] = (
    "akira",
    "play",
    "qilin",
    "thegentlemen",
    "incransom",
)

CONFIG_SECTION = "ransomwarelive"


def read_api_config(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")
    if not cp.has_section(CONFIG_SECTION):
        return {}
    out: dict[str, str] = {}
    if cp.has_option(CONFIG_SECTION, "api_key"):
        v = cp.get(CONFIG_SECTION, "api_key", fallback="").strip()
        if v and v.lower() not in ("paste-your-api-key-here", ""):
            out["api_key"] = v
    if cp.has_option(CONFIG_SECTION, "api_base"):
        b = cp.get(CONFIG_SECTION, "api_base", fallback="").strip().rstrip("/")
        if b:
            out["api_base"] = b
    return out


def resolve_api_key_and_base() -> tuple[str, str]:
    cfg = read_api_config(CONFIG_PATH)
    key = (cfg.get("api_key") or "").strip()
    if not key:
        key = (os.environ.get("RANSOMWARELIVE_API_KEY", "") or "").strip()
    base = os.environ.get("RANSOMWARELIVE_API_BASE", "").strip().rstrip("/")
    if not base:
        base = (cfg.get("api_base") or "").strip().rstrip("/")
    if not base:
        base = API_BASE_DEFAULT.rstrip("/")
    return key, base


def api_request(
    path: str,
    api_key: str,
    params: dict | None = None,
    timeout: float = 120.0,
    base: str | None = None,
) -> object:
    root = (base or API_BASE_ENV).rstrip("/")
    url = root + path
    if params:
        q = {k: v for k, v in params.items() if v is not None and v != ""}
        if q:
            url += "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(
        url,
        headers={
            "X-API-KEY": api_key,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:2000]
        raise SystemExit(f"HTTP {e.code} for {url}\n{detail}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Request failed: {url}\n{e}") from e
    if not body.strip():
        return None
    return json.loads(body)


def normalize_victims_payload(data: object) -> list[dict]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("victims", "data", "results", "items"):
            inner = data.get(key)
            if isinstance(inner, list):
                return [x for x in inner if isinstance(x, dict)]
    return []


def sector_label(v: dict) -> str:
    a = v.get("activity") or v.get("sector")
    s = str(a).strip() if a is not None else ""
    return s if s else "(unknown sector)"


def country_label(v: dict) -> str:
    c = v.get("country")
    s = str(c).strip().upper() if c is not None else ""
    return s if s else "(unknown country)"


def aggregate_group_victims(victims: list[dict]) -> dict:
    by_sector = Counter()
    by_country = Counter()
    sector_country: Counter[tuple[str, str]] = Counter()
    for v in victims:
        sec = sector_label(v)
        cc = country_label(v)
        by_sector[sec] += 1
        by_country[cc] += 1
        sector_country[(sec, cc)] += 1
    return {
        "victim_records": len(victims),
        "by_sector": dict(by_sector.most_common()),
        "by_country": dict(by_country.most_common()),
        "sector_by_country": {
            f"{a}|{b}": n for (a, b), n in sector_country.most_common()
        },
    }


def build_wide_matrix(per_group: dict[str, dict]) -> tuple[list[str], list[str], list[list[int]]]:
    sectors: set[str] = set()
    for gdata in per_group.values():
        sectors.update((gdata.get("by_sector") or {}).keys())
    sector_cols = sorted(sectors)
    group_rows = sorted(per_group.keys())
    matrix: list[list[int]] = []
    for g in group_rows:
        row = [(per_group[g].get("by_sector") or {}).get(s, 0) for s in sector_cols]
        matrix.append(row)
    return group_rows, sector_cols, matrix


def write_csv_matrix(
    path: Path,
    row_labels: list[str],
    col_labels: list[str],
    matrix: list[list[int]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group"] + col_labels)
        for i, g in enumerate(row_labels):
            w.writerow([g] + [matrix[i][j] for j in range(len(col_labels))])


def main() -> None:
    key, api_base = resolve_api_key_and_base()
    if not key:
        print(
            "Missing API key: set api_key in api_config.ini (see api_config.example.ini) "
            "or set RANSOMWARELIVE_API_KEY.",
            file=sys.stderr,
        )
        sys.exit(1)

    groups = list(GROUP_SLUGS)
    print(f"Fetching heatmap data for {len(groups)} groups: {', '.join(groups)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_group: dict[str, dict] = {}
    meta = {
        "api_base": api_base,
        "group_count": len(groups),
        "groups": groups,
    }

    n = len(groups)
    for i, g in enumerate(groups):
        print(f"  [{i + 1}/{n}] victims for {g}…", flush=True)
        victims_raw = api_request("/victims/", key, params={"group": g}, base=api_base)
        victims = normalize_victims_payload(victims_raw)
        agg = aggregate_group_victims(victims)
        agg["group"] = g
        per_group[g] = agg
        if i + 1 < n and REQUEST_SLEEP_SEC > 0:
            time.sleep(REQUEST_SLEEP_SEC)

    row_labels, col_labels, matrix = build_wide_matrix(per_group)
    bundle = {
        "meta": meta,
        "per_group": per_group,
        "heatmap_matrix": {
            "rows": row_labels,
            "columns": col_labels,
            "counts": matrix,
        },
    }

    json_path = OUT_DIR / "heatmap_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    csv_path = OUT_DIR / "heatmap_sector_matrix.csv"
    write_csv_matrix(csv_path, row_labels, col_labels, matrix)

    print(f"Done — wrote {json_path}")
    print(f"         {csv_path}")


if __name__ == "__main__":
    main()
