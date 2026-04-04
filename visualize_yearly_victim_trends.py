#!/usr/bin/env python3
"""
Plot how victim counts per group change by calendar year, using API victim records.
Uses the same groups and api_config.ini as fetch_api_heatmap_data.py.

Year is taken from the victim's discovered date when present, otherwise attack date.

Run (needs network + valid API key):
  python visualize_yearly_victim_trends.py
"""

from __future__ import annotations

import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fetch_api_heatmap_data import (
    GROUP_SLUGS,
    REQUEST_SLEEP_SEC,
    api_request,
    normalize_victims_payload,
    resolve_api_key_and_base,
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_PNG = SCRIPT_DIR / "output" / "victim_trends_by_year.png"
OUT_CSV = SCRIPT_DIR / "output" / "api_heatmap" / "victims_by_year.csv"


def year_from_record(v: dict) -> int | None:
    for key in ("discovered", "attackdate"):
        val = v.get(key)
        if not val:
            continue
        s = str(val).strip()
        if len(s) >= 4 and s[:4].isdigit():
            y = int(s[:4])
            if 1990 <= y <= 2100:
                return y
    return None


def main() -> None:
    key, api_base = resolve_api_key_and_base()
    if not key:
        print(
            "Missing API key: api_config.ini or RANSOMWARELIVE_API_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    by_group_year: dict[str, dict[int, int]] = {g: defaultdict(int) for g in GROUP_SLUGS}
    n_groups = len(GROUP_SLUGS)

    for i, g in enumerate(GROUP_SLUGS):
        print(f"[{i + 1}/{n_groups}] {g}…", flush=True)
        raw = api_request("/victims/", key, params={"group": g}, base=api_base)
        victims = normalize_victims_payload(raw)
        for v in victims:
            y = year_from_record(v)
            if y is not None:
                by_group_year[g][y] += 1
        if i + 1 < n_groups and REQUEST_SLEEP_SEC > 0:
            time.sleep(REQUEST_SLEEP_SEC)

    all_years: set[int] = set()
    for d in by_group_year.values():
        all_years.update(d.keys())
    if not all_years:
        raise SystemExit("No years parsed from victim records.")

    years = sorted(all_years)
    x = np.array(years, dtype=float)

    fig, ax = plt.subplots(figsize=(11, 6))
    palette = plt.cm.tab10.colors
    for idx, g in enumerate(GROUP_SLUGS):
        counts = np.array([by_group_year[g].get(y, 0) for y in years])
        ax.plot(
            x,
            counts,
            marker="o",
            linewidth=2.2,
            markersize=6,
            label=g,
            color=palette[idx % len(palette)],
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Victim count")
    ax.set_title("Victim counts by year and group")
    if len(years) > 12:
        step = max(1, len(years) // 12)
        tick_years = years[::step]
        ax.set_xticks(tick_years)
        ax.set_xticklabels([str(int(y)) for y in tick_years], rotation=0, ha="center")
    else:
        ax.set_xticks(years)
        ax.set_xticklabels([str(int(y)) for y in years], rotation=0, ha="center")
    ax.legend(title="Group", loc="best", fontsize=9)
    ax.grid(True, alpha=0.35, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(GROUP_SLUGS))
        for y in years:
            w.writerow([y] + [by_group_year[g].get(y, 0) for g in GROUP_SLUGS])

    print(f"Wrote {OUT_PNG}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
