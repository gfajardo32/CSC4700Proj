# Ransomware Group Analysis — CSC4700

## Abstract

Ransomware continues to pose a significant and evolving threat to organizations worldwide, with
increasing frequency, sophistication, and financial impact. This project investigates ransomware
activity by focusing on five active cybercriminal groups — Qilin, TheGentleMan, Akira, Incransom,
and Play — selected based on their recent activity and relevance. Using real-world victim data from
ransomware tracking platforms, the study examines patterns in sector targeting, geographic
distribution, and operational behaviors of these groups.

The analysis highlights a strong concentration of attacks in the manufacturing and construction
sectors, with additional targeting of healthcare and business services. Beyond quantitative trends,
the project integrates qualitative insights, including case-based analysis of victim organizations,
financial impacts, and attack methodologies. The ultimate goal is to identify sector-specific
vulnerabilities, understand attacker strategies, and provide actionable insights into ransomware
defense and mitigation.

## Introduction

Ransomware has become one of the most disruptive and costly forms of cybercrime. It has evolved
from simple malware into a structured criminal business model focused on extortion, data theft, and
large-scale operations. According to the FBI's Internet Crime Complaint Center (IC3), ransomware
remained the most significant threat to U.S. critical infrastructure in 2024, with incidents continuing
to increase each year. Similarly, the Verizon 2024 Data Breach Investigations Report (DBIR) shows
that ransomware and extortion attacks make up a large portion of financially motivated breaches and
affect most industries.

The period between 2024 and 2025 shows an important shift in ransomware activity. Although total
ransomware payments dropped to about $813 million in 2024 compared to 2023, this does not mean
the threat has decreased. Instead, attackers are changing their strategies to use faster and more
efficient methods, such as stealing data without encrypting it. This shift shows that ransomware
groups are adapting to law enforcement actions and stronger security defenses.

Manufacturing has remained one of the most targeted sectors for several years because it cannot
afford downtime and is more likely to pay ransoms. Healthcare is another high-risk sector — incidents
like the Change Healthcare cyberattack show how ransomware can disrupt critical services and have
wide-reaching impacts. In 2025, groups such as Qilin, Akira, Play, and INC Ransom remain very
active, often targeting dozens of victims each month, using phishing, exploiting exposed systems,
credential theft, and misuse of legitimate tools.

This project focuses on five ransomware groups — Qilin, TheGentleMan, Akira, Incransom, and
Play — and analyzes their victim data to identify patterns across sectors, geographies, and attack
behaviors. The approach combines quantitative data analysis with qualitative case-based insights to
support better understanding of ransomware threats and defenses.

## Project Structure

```
CSC4700Proj/
├── code/                       Python scripts
├── CSVs/                       CSV output files
├── json/                       JSON group profile files
├── qualitative_research.md     Qualitative analysis notes
└── README.md
```

## Scripts

### code/groupGenRequest.py

Fetches group profile data from the ransomware.live API v2 for each of the five groups and saves
the raw JSON response per group.

**Output:** `json/{group}_group.json` for each of the five groups.

**Run:**
```
python code/groupGenRequest.py
```

---

### code/dataCollection.py

Scrapes the ransomware.live group pages to collect summary statistics per group: total victims,
top 5 activity sectors, and top 5 countries.

**Output:** `CSVs/group_summary.csv`

**Run:**
```
python code/dataCollection.py
```

---

### code/ransomware_research.py

Main analysis script. Fetches all victims for each group from the API, filters for manufacturing
sector victims, searches Google News RSS for real-world impact coverage, and checks for victim
overlap across groups.

**Output:**

| File | Contents |
|---|---|
| `CSVs/all_victims.csv` | Every victim across all five groups |
| `CSVs/manufacturing_victims.csv` | Manufacturing-sector subset |
| `CSVs/news_hits.csv` | Google News articles per manufacturing victim |
| `CSVs/victim_overlap.csv` | Victims claimed by two or more groups |

**Run:**
```
python code/ransomware_research.py
```

## Requirements

Install dependencies before running any script:

```
pip install -r code/requirements.txt
```

## Groups Studied

| Group | Notes |
|---|---|
| Qilin | High volume, broad sector targeting |
| TheGentleMan | Active across manufacturing and construction |
| Akira | Consistent activity, targets SMBs and enterprise |
| Incransom | Notable focus on healthcare |
| Play | Structured operations, targets multiple sectors |

## Data Source

Victim data is sourced from [ransomware.live](https://ransomware.live), a public platform that
aggregates ransomware group activity from leak sites and reporting sources.
