# Qualitative Research: Real-World Ransomware Impact
## Multi-Group Victim Analysis — Qilin, Play, Akira, Incransom

> **Research focus:** Companies identified as victims of **two or more** of our tracked threat groups.
> These overlap cases are particularly significant — they demonstrate that threat actors may share
> intelligence, purchase stolen data from each other, or independently identify the same high-value targets.

---

## Sector Context: Why Manufacturing Gets Hit Hardest

Before diving into individual cases, it helps to understand the macro picture:

- **65%** of manufacturing organizations were hit by ransomware in 2024 — the highest rate of any industry
- **62%** of manufacturing victims paid the ransom — also the highest of any sector
- Ransomware has cost the manufacturing sector an estimated **$17 billion in downtime** since 2018
- Average downtime per manufacturing incident: **11 days** at a cost of ~**$1.9M per day**
- Median ransom payment in manufacturing in 2024: **$1.2 million**
- Average total cost of a ransomware attack (all sectors) in 2024: **$5.13 million**

Manufacturing is targeted because of its low downtime tolerance (production halts = immediate revenue loss),
broad attack surfaces (OT/IT convergence), and the high sensitivity of the operational data attackers can steal.

---

## Case 1: Bunger Steel — Play + Qilin

| Field | Details |
|---|---|
| **Company** | Bunger Steel, Inc. |
| **Location** | Phoenix, Arizona, USA |
| **Founded** | 1974 |
| **Industry** | Steel manufacturing & building components |
| **Size** | ~92 employees |
| **Annual Revenue** | ~$47.7 million |
| **Groups** | Play (primary), Qilin |
| **Attack Date** | November 5, 2024 (Play claim) |

### What Happened
Play ransomware claimed responsibility for an attack on Bunger Steel — Arizona's largest steel building
and components vendor in the southwestern United States. The group published the victim on their dark web
leak site, employing their standard double-extortion model: encrypt systems AND threaten to release
stolen data publicly if the ransom is not paid.

Qilin separately listed Bunger Steel as a victim, making this one of the clearest cross-group targeting
cases in our dataset.

### Data Compromised
Attackers claimed to have exfiltrated a broad range of sensitive business data including:
- Client documents and contracts
- Payroll records
- Accounting and financial information
- Internal business records

### Impact Assessment
While Bunger Steel has not made a public statement, the exposure of payroll and financial records
for a ~$47.7M revenue company carries serious downstream risk: employee identity theft, legal
liability, and loss of client trust. The fact that two separate ransomware groups listed this company
suggests the breach may have involved data being re-sold or shared across the criminal ecosystem.

---

## Case 2: Burnham Brown — Qilin + Incransom

| Field | Details |
|---|---|
| **Company** | Burnham Brown |
| **Location** | Oakland, California, USA |
| **Industry** | Law firm (serves manufacturing, construction, healthcare clients) |
| **Groups** | Qilin, Incransom |
| **First Attack** | November 26, 2025 (Qilin) |
| **Second Attack** | December 31, 2025 (Incransom) |

> ⚠️ **Note for presentation:** Burnham Brown is a law firm, not a manufacturer — however, it appears
> in our manufacturing-adjacent victim overlap because it serves manufacturing and construction clients.
> This is a compelling case to highlight: **ransomware groups targeting legal firms to get to their
> industrial clients.**

### What Happened
Burnham Brown — a full-service law firm with clients across manufacturing, construction, commercial
real estate, transportation, and healthcare — was struck by Qilin ransomware on November 26, 2025.
Less than 6 weeks later, on December 31, 2025, the same firm was hit again by Incransom ransomware.

This is a textbook example of a "double hit" — the first breach likely exposed vulnerabilities that
a second group exploited, or the stolen data was traded on the dark web and re-used.

### Data Compromised
According to disclosures on the groups' dark web leak portals:
- Confidential legal documents and internal records
- Privileged attorney–client correspondence
- Client case files and financial records
- Sensitive materials belonging to the firm's manufacturing and construction-sector clients

### Why This Matters
Law firms are prime ransomware targets because of the uniquely sensitive nature of the data they
hold — privileged communications, NDAs, litigation strategy, and financial records across entire
client portfolios. A breach here doesn't just hurt the firm; it exposes every client whose documents
were stored on their systems.

---

## Case 3: Cottage — Play + Qilin

| Field | Details |
|---|---|
| **Company** | Cottage (exact entity unconfirmed) |
| **Groups** | Play, Qilin |
| **Public Coverage** | Limited |

### What Happened
"Cottage" appears in our dataset as a victim of both the Play and Qilin ransomware groups. Public
reporting on this specific company is limited — a common pattern for smaller manufacturing victims who
do not issue press statements and whose incidents don't attract major media coverage.

The dual-group listing is notable: both Play and Qilin are among the top 5 most active ransomware
groups globally in 2024–2025. When two top-tier groups independently list the same victim, it strongly
suggests the target held high-value data, or that the initial breach data was traded between groups.

### Broader Context
Play ransomware breached over 900 organizations through mid-2025 per FBI figures, with 80% of
its 2024 attacks targeting US entities. Qilin claimed 1,034 victims in 2025 alone, publishing at a
rate of over 40 new victims per month.

---

## Case 4: J.M. Thompson Company — Qilin + Play

| Field | Details |
|---|---|
| **Company** | J.M. Thompson Company |
| **Location** | Cary, North Carolina, USA |
| **Founded** | 1921 |
| **Industry** | General contractor (serves manufacturing, healthcare, education, government) |
| **Size** | 20–49 employees |
| **Annual Revenue** | $10M–$25M (estimated) |
| **Groups** | Qilin (confirmed), Play |
| **Attack Date** | ~August–September 2024 (Qilin deadline: September 5, 2024) |

### What Happened
J.M. Thompson Company, a commercial construction and contracting firm with over 100 years of
operating history, was claimed by Qilin ransomware with a public deadline of **September 5, 2024**
to pay or have their data released. Qilin (also known as "Agenda") posted the victim on their
dark web leak site, threatening to publish sensitive organizational data.

The firm also appears in Play's victim data, again suggesting cross-group data sharing or
independent opportunistic targeting.

### Data at Risk
As a contractor serving healthcare, manufacturing, and government clients, J.M. Thompson's data
would include building plans, project contracts, subcontractor records, client contact details, and
potentially security-sensitive facility layout information for regulated industries.

### Public Response
No public statement has been located from J.M. Thompson. This is consistent with the broader
pattern of small-to-mid-size contractors: without a legal obligation to disclose (unlike healthcare
or finance), many simply absorb the attack quietly — paying the ransom or restoring from backups
without informing clients or the public.

---

## Case 5: Maxus Group — Akira + Play

| Field | Details |
|---|---|
| **Company** | Maxus Group |
| **Industry** | Contractor / industrial services |
| **Groups** | Akira (primary), Play |
| **Discovery Date** | November 18, 2024 (Akira listing) |

### What Happened
Maxus Group was listed on Akira ransomware's dark web leak site on November 18, 2024. Akira,
which emerged in March 2023 and has since targeted over 250+ organizations globally, employs
a double-extortion model and primarily exploits Cisco VPN products — particularly where
multi-factor authentication is not enforced.

Maxus Group also appears as a Play victim, making it one of our clearest examples of cross-group
activity in the dataset.

### Data Compromised
The Akira leak page for Maxus Group disclosed particularly sensitive data:
- Non-Disclosure Agreements (NDAs) with contractor partners
- Social Security Numbers (SSNs) of employees or contractors
- Contact details of staff and clients
- Financial records including credit card CVV data

### Impact Assessment
The exposure of SSNs and CVV financial data represents direct, actionable harm to individuals —
not just the company. Affected employees and contractors face identity theft and financial fraud
risk. For the company itself, this creates legal liability under state and federal breach
notification laws. The NDA leak also exposes proprietary business relationships that were
explicitly meant to remain confidential.

---

## Key Takeaways for Presentation

1. **Cross-group targeting is real.** All 5 of our overlap companies were claimed by 2 different
   ransomware groups. This suggests either data re-sale between criminal actors or independently
   opportunistic attacks against the same soft targets.

2. **Small-to-mid-size companies are disproportionately exposed.** None of these companies are
   enterprise-scale. Revenues range from $10M to $47.7M, with small IT teams unlikely to have
   mature incident response capabilities.

3. **Public silence is the norm.** None of the 5 companies issued public statements. This
   underreporting masks the true scale of the problem.

4. **The data stolen goes beyond operations.** Payroll records, SSNs, CVV data, and legal documents
   mean that ransomware attacks on contractors and manufacturers cascade into personal harm for
   employees and clients — not just business disruption.

5. **Manufacturing + law/contracting supply chain = high-value target cluster.** Burnham Brown
   and J.M. Thompson show that attackers don't always go directly after the manufacturer — they
   target the supply chain and legal ecosystem around it.

---

## Sources

- [Play Ransomware Group Targets Bunger Steel — Halcyon](https://www.halcyon.ai/attacks/play-ransomware-group-targets-bunger-steel-compromises-data)
- [Incransom Ransomware Victim: Burnham Brown — RedPacket Security](https://www.redpacketsecurity.com/incransom-ransomware-victim-burnham-brown/)
- [FalconFeeds — Burnham Brown double hit (Qilin + Incransom)](https://x.com/FalconFeedsio/status/2006316150783910321)
- [Burnham Brown Data Breach — Hookphish](https://www.hookphish.com/blog/ransomware-group-incransom-hits-burnham-brown/)
- [Qilin Ransomware Hits J.M. Thompson — Halcyon](https://www.halcyon.ai/attacks/qilin-ransomware-hits-j-m-thompson-cybersecurity-alert)
- [Akira Ransomware Victim: Maxus Group — RedPacket Security](https://www.redpacketsecurity.com/akira-ransomware-victim-maxus-group/)
- [FBI: Play Ransomware Breached 900 Victims — BleepingComputer](https://www.bleepingcomputer.com/news/security/fbi-play-ransomware-breached-900-victims-including-critical-orgs/)
- [Ransomware Costs Manufacturing Sector $17bn in Downtime — Infosecurity Magazine](https://www.infosecurity-magazine.com/news/ransomware-manufacturing-dollar17b/)
- [Ransomware Attacks Set New Records in 2025, Hitting Manufacturing Hardest — Smart Industry](https://www.smartindustry.com/industry-news/news/55352408/ransomware-attacks-set-new-records-in-2025-hitting-manufacturing-the-hardest)
- [The State of Ransomware Q3 2025 — Check Point Research](https://research.checkpoint.com/2025/the-state-of-ransomware-q3-2025/)
- [Qilin Ransomware: Analysis, Impact and Defense 2025 — BlackFog](https://www.blackfog.com/qilin-ransomware-analysis-impact-and-defense-2025/)
- [#StopRansomware: Akira — CISA](https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-109a)
