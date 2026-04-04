#!/usr/bin/env python3
"""
Generate charts from group_summary.csv and *_group.json in this directory.
Outputs PNGs under ./output/
"""

from __future__ import annotations

import json
import re
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
CSV_PATH = BASE / "group_summary.csv"

# Human-readable axis labels for infra types (raw values are short codes from the dataset)
LOCATION_TYPE_LABELS: dict[str, str] = {
    "DLS": "DLS — data leak site",
    "Chat": "Chat — negotiation / contact",
    "Admin": "Admin — operator panel",
    "Unknown": "Unknown",
}

# Tool buckets classify reported tooling by role in an intrusion (same names as the dataset keys)
TOOL_CATEGORY_LABELS: dict[str, str] = {
    "CredentialTheft": "Credential theft",
    "DefenseEvasion": "Defense evasion",
    "DiscoveryEnum": "Discovery & enumeration",
    "Exfiltration": "Exfiltration",
    "LOLBAS": "LOLBAS (living-off-the-land)",
    "Networking": "Networking / tunnels",
    "Offsec": "Offensive security",
    "RMM-Tools": "Remote access (RMM)",
}


def wrap_tick_label(text: object, width: int = 14) -> str:
    """Multi-line label for horizontal (rotation=0) x-axis ticks without overlap."""
    s = str(text).strip()
    if len(s) <= width:
        return s
    return "\n".join(
        textwrap.wrap(s, width=width, break_long_words=False, break_on_hyphens=False)
    )


def format_heatmap_sector_label(sector: str) -> str:
    """Sector heatmap: put each side of '/' on its own line (e.g. Transportation / Logistics)."""
    s = str(sector).strip()
    if "/" in s:
        parts = [p.strip() for p in s.split("/") if p.strip()]
        if len(parts) > 1:
            return "\n".join(parts)
    return wrap_tick_label(s, width=11)


def parse_label_count(field: str) -> list[tuple[str, int]]:
    """Parse 'Name 12, Other Name 3' into [('Name', 12), ...]."""
    if not isinstance(field, str) or not field.strip():
        return []
    parts = re.split(r",\s*", field.strip())
    out: list[tuple[str, int]] = []
    for p in parts:
        m = re.match(r"^(.+?)\s+(\d+)$", p.strip())
        if m:
            out.append((m.group(1).strip(), int(m.group(2))))
    return out


def primary_name(field: str) -> str | None:
    if not isinstance(field, str) or not field.strip():
        return None
    m = re.match(r"^(.+?)\s+\d+$", field.strip())
    return m.group(1).strip() if m else field.strip()


def load_group_json(name: str) -> dict:
    path = BASE / f"{name}_group.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tactic_technique_counts(data: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for block in data.get("ttps") or []:
        tname = block.get("tactic_name") or block.get("tactic_id") or "Unknown"
        n = len(block.get("techniques") or [])
        counts[tname] = counts.get(tname, 0) + n
    return counts


def tool_category_counts(data: dict) -> dict[str, int]:
    tools = data.get("tools") or []
    if not tools or not isinstance(tools[0], dict):
        return {}
    out: dict[str, int] = {}
    for cat_dict in tools:
        for cat, items in cat_dict.items():
            if isinstance(items, list):
                out[cat] = out.get(cat, 0) + len(items)
    return out


def location_type_counts(data: dict) -> dict[str, int]:
    c: Counter[str] = Counter()
    for loc in data.get("locations") or []:
        t = loc.get("type") or "Unknown"
        c[str(t)] += 1
    return dict(c)


def plot_top5_sectors_per_group(df: pd.DataFrame) -> None:
    n = len(df)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 5.8), squeeze=False)
    primary_color = "#c0392b"
    other_color = "#3498db"

    for ax, (_, row) in zip(axes[0], df.iterrows()):
        sectors = parse_label_count(row["top_5_sectors"])
        prim = primary_name(row["primary_sector"])
        if len(sectors) > 5:
            sectors = sectors[:5]
        names = [s[0] for s in sectors]
        vals = [s[1] for s in sectors]
        colors = [primary_color if s[0] == prim else other_color for s in sectors]

        x = np.arange(len(names))
        ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("Victim count")
        ax.set_title(str(row["group_name"]).upper(), fontweight="bold")
        ax.set_ylim(0, max(vals) * 1.15 if vals else 1)

    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=primary_color, label="Primary sector"),
        plt.Rectangle((0, 0), 1, 1, fc=other_color, label="Other top sectors"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Top five targeted sectors by group", y=1.05)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(OUT / "01_top5_sectors_per_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_victim_counts(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    names = df["group_name"].tolist()
    counts = df["total_victims"].astype(int).tolist()
    x = np.arange(len(names))
    ax.bar(x, counts, color="#2ecc71", width=0.65)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=0, ha="center")
    ax.set_ylabel("Victim count")
    ax.set_title("Victim count by group")
    fig.tight_layout()
    fig.savefig(OUT / "02_victim_counts_per_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_top5_countries_per_group(df: pd.DataFrame) -> None:
    n = len(df)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 5.8), squeeze=False)
    c_primary = "#e67e22"
    c_other = "#95a5a6"
    for ax, (_, row) in zip(axes[0], df.iterrows()):
        countries = parse_label_count(row["top_5_countries"])
        prim = primary_name(row["primary_country"])
        if len(countries) > 5:
            countries = countries[:5]
        names = [c[0] for c in countries]
        vals = [c[1] for c in countries]
        colors = [c_primary if c[0] == prim else c_other for c in countries]
        x = np.arange(len(names))
        ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(
            [wrap_tick_label(n, width=12) for n in names],
            rotation=0,
            ha="center",
            fontsize=8,
        )
        ax.set_ylabel("Victim count")
        ax.set_title(str(row["group_name"]).upper(), fontweight="bold")
        ax.set_ylim(0, max(vals) * 1.12 if vals else 1)
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=c_primary, label="Primary country"),
        plt.Rectangle((0, 0), 1, 1, fc=c_other, label="Other top countries"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Top five targeted countries by group", y=1.08)
    fig.tight_layout()
    fig.savefig(OUT / "03_top5_countries_per_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_sector_heatmap(df: pd.DataFrame) -> None:
    """Rows = groups, columns = union of top-5 sector names (sparse matrix)."""
    sector_by_group: dict[str, dict[str, int]] = {}
    all_sectors: set[str] = set()
    for _, row in df.iterrows():
        g = str(row["group_name"])
        d = {s: v for s, v in parse_label_count(row["top_5_sectors"])}
        sector_by_group[g] = d
        all_sectors.update(d.keys())
    sectors_sorted = sorted(all_sectors)
    groups = df["group_name"].astype(str).tolist()
    mat = np.zeros((len(groups), len(sectors_sorted)))
    for i, g in enumerate(groups):
        for j, s in enumerate(sectors_sorted):
            mat[i, j] = sector_by_group.get(g, {}).get(s, 0)

    fig, ax = plt.subplots(figsize=(max(10, len(sectors_sorted) * 0.45), 5.8))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(np.arange(len(sectors_sorted)))
    ax.set_xticklabels(
        [format_heatmap_sector_label(s) for s in sectors_sorted],
        rotation=0,
        ha="center",
        fontsize=7,
    )
    ax.set_yticks(np.arange(len(groups)))
    ax.set_yticklabels(groups)
    ax.set_title("Sector victim counts by group (top five sectors)")
    plt.colorbar(im, ax=ax, label="Count")
    fig.tight_layout()
    fig.savefig(OUT / "04_sector_heatmap_groups.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_mitre_tactics_stacked(json_by_group: dict[str, dict]) -> None:
    """Stacked horizontal bar: each group shows technique counts per MITRE tactic."""
    tactic_names: set[str] = set()
    per_group: dict[str, dict[str, int]] = {}
    for g, data in json_by_group.items():
        c = tactic_technique_counts(data)
        per_group[g] = c
        tactic_names.update(c.keys())
    tactics = sorted(tactic_names)
    groups = list(per_group.keys())
    bottom = np.zeros(len(groups))
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = plt.cm.tab20.colors
    for i, t in enumerate(tactics):
        vals = np.array([per_group[g].get(t, 0) for g in groups])
        if vals.sum() == 0:
            continue
        ax.barh(groups, vals, left=bottom, label=t, color=palette[i % len(palette)])
        bottom = bottom + vals
    ax.set_xlabel("Technique entries per tactic")
    ax.set_title("MITRE ATT&CK tactics: technique counts by group")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "05_mitre_tactics_stacked_by_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_tool_categories(json_by_group: dict[str, dict]) -> None:
    """Grouped bar: tool-category totals per group."""
    cats: set[str] = set()
    per: dict[str, dict[str, int]] = {}
    for g, data in json_by_group.items():
        d = tool_category_counts(data)
        per[g] = d
        cats.update(d.keys())
    if not cats:
        return
    categories = sorted(cats)
    cat_labels = [TOOL_CATEGORY_LABELS.get(c, c) for c in categories]
    groups = list(per.keys())
    x = np.arange(len(categories))
    w = 0.8 / max(len(groups), 1)
    fig, ax = plt.subplots(figsize=(max(8, len(categories) * 0.55), 5.8))
    for i, g in enumerate(groups):
        offset = (i - len(groups) / 2) * w + w / 2
        heights = [per[g].get(c, 0) for c in categories]
        ax.bar(x + offset, heights, w * 0.9, label=g)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("Listed tools (count)")
    ax.set_title("Reported tool types by group")
    ax.legend(title="Group", fontsize=8)
    fig.tight_layout(rect=(0, 0.18, 1, 1))
    fig.savefig(OUT / "06_tool_categories_by_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_location_types(json_by_group: dict[str, dict]) -> None:
    types: set[str] = set()
    per: dict[str, dict[str, int]] = {}
    for g, data in json_by_group.items():
        d = location_type_counts(data)
        per[g] = d
        types.update(d.keys())
    if not types:
        return
    preferred = ["DLS", "Chat", "Admin"]
    type_list = [t for t in preferred if t in types] + sorted(
        t for t in types if t not in preferred
    )
    type_labels = [LOCATION_TYPE_LABELS.get(t, t) for t in type_list]
    groups = list(per.keys())
    x = np.arange(len(type_list))
    w = 0.8 / max(len(groups), 1)
    fig, ax = plt.subplots(figsize=(max(7.5, len(type_list) * 0.65), 5.5))
    for i, g in enumerate(groups):
        offset = (i - len(groups) / 2) * w + w / 2
        heights = [per[g].get(t, 0) for t in type_list]
        ax.bar(x + offset, heights, w * 0.9, label=g)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [wrap_tick_label(lab, width=18) for lab in type_labels],
        rotation=0,
        ha="center",
        fontsize=8,
    )
    ax.set_ylabel("Known endpoints")
    ax.set_title("Public infrastructure by type")
    ax.legend(title="Group", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "07_location_types_by_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_raas_flags(json_by_group: dict[str, dict]) -> None:
    labels = []
    values = []
    for g, data in sorted(json_by_group.items()):
        t = data.get("type") or {}
        raas = bool(t.get("raas")) if isinstance(t, dict) else False
        labels.append(g)
        values.append(1 if raas else 0)
    if not labels:
        return
    fig, ax = plt.subplots(figsize=(6, 3))
    colors = ["#27ae60" if v else "#bdc3c7" for v in values]
    ax.barh(labels, values, color=colors)
    ax.set_xlim(-0.1, 1.2)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["No", "Yes"])
    ax.set_xlabel("Ransomware-as-a-service (RaaS) model")
    ax.set_title("RaaS model reported by group")
    fig.tight_layout()
    fig.savefig(OUT / "08_raas_flag_by_group.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_share_of_primary_sector(df: pd.DataFrame) -> None:
    """Primary-sector victim count as % of each group's total victim count."""
    rows: list[tuple[str, float, int, int]] = []
    for _, row in df.iterrows():
        sectors = parse_label_count(row["top_5_sectors"])
        prim = primary_name(row["primary_sector"])
        total_victims = int(row["total_victims"])
        prim_v = next((v for s, v in sectors if s == prim), 0)
        pct = 100.0 * prim_v / total_victims if total_victims else 0.0
        rows.append((str(row["group_name"]), pct, prim_v, total_victims))
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    names = [r[0] for r in rows]
    pcts = [r[1] for r in rows]
    x = np.arange(len(names))
    ax.bar(x, pcts, color="#16a085")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=0, ha="center")
    ax.set_ylabel("Percent of all victims")
    ax.set_title("Victims in the primary sector (share of total)")
    top = max(pcts) if pcts else 0.0
    ax.set_ylim(0, top * 1.18 if top > 0 else 1.0)
    for i, r in enumerate(rows):
        ax.annotate(
            f"{r[2]} / {r[3]}\nvictims",
            (x[i], pcts[i]),
            ha="center",
            va="bottom",
            fontsize=7,
            linespacing=1.1,
        )
    fig.tight_layout()
    fig.savefig(OUT / "09_primary_sector_share_of_top5.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    df = df.sort_values("group_name").reset_index(drop=True)

    json_by_group: dict[str, dict] = {}
    for name in df["group_name"].astype(str):
        json_by_group[name] = load_group_json(name)

    plot_top5_sectors_per_group(df)
    plot_victim_counts(df)
    plot_top5_countries_per_group(df)
    plot_sector_heatmap(df)
    plot_mitre_tactics_stacked(json_by_group)
    plot_tool_categories(json_by_group)
    plot_location_types(json_by_group)
    plot_raas_flags(json_by_group)
    plot_share_of_primary_sector(df)

    print(f"Wrote charts to {OUT}/")


if __name__ == "__main__":
    main()
