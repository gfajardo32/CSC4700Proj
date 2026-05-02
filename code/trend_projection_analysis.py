import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy import stats

df = pd.read_csv("all_victims.csv")

#Filter for rows with visible attackdates only
df["attackdate"] = pd.to_datetime(df["attackdate"], errors="coerce")
df = df.dropna(subset=["attackdate"])

df = df[df["attackdate"] >= "2023-01-01"]

df["month"] = df["attackdate"].dt.to_period("M")

GROUPS = ["qilin", "thegentlemen", "akira", "incransom", "play"]
COLORS = {
    "qilin": "blue",
    "thegentlemen": "green",
    "akira": "olive",
    "incransom": "orange",
    "play": "red"
}

GROUP_START_DATES = {
    "qilin":        "2023-01-01",
    "thegentlemen": "2025-06-01",  # meaningful activity  for thegentlen only starts here
    "akira":        "2023-04-01",
    "incransom":    "2023-06-01",
    "play":         "2022-12-01"
}

#Qualitative case annotations
ANNOTATIONS = {
    "play": [
        ("2024-06-07", "Bunger Steel", 30),
        ("2024-03-14", "JM Thompson", 40),
        ("2024-12-12", "Maxus Group", 30),
    ],
    "qilin": [
        ("2024-06-23", "Bunger Steel", 15),
        ("2024-08-24", "JM Thompson", 25),
        ("2025-11-26", "Burnham Brown", 80),
    ],
    "akira": [
        ("2024-09-02", "Maxus Group", 65),
    ],
    "incransom": [
        ("2025-12-31", "Burnham Brown", 40),
    ]
}

fig, axes = plt.subplots(3, 2, figsize=(22, 20))
axes = axes.flatten()
fig.suptitle("Ransomware Victim Trends with 6-Month Projection", fontsize=14, fontweight="bold", y=.98)

projection_months = 6

for i, group in enumerate(GROUPS):
    ax = axes[i]
    start_date = GROUP_START_DATES.get(group, "2023-01-01")
    group_df = df[(df["group"] == group) & (df["attackdate"] >= start_date)]

    # Count victims per month
    monthly = group_df.groupby("month").size().reset_index(name="count")
    monthly["month_ts"] = monthly["month"].dt.to_timestamp()
    monthly = monthly.sort_values("month_ts")

    median_count = monthly["count"].median()
    monthly["count"] = monthly["count"].clip(upper=median_count * 3)

    if len(monthly) < 3:
        ax.set_title(f"{group.capitalize()} — insufficient data")
        continue

    # Convert dates to numeric for regression
    x_numeric = np.arange(len(monthly))
    y = monthly["count"].values

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, y)
    trend_line = slope * x_numeric + intercept

    # Project forward 6 months
    x_future = np.arange(len(monthly), len(monthly) + projection_months)
    y_future = slope * x_future + intercept
    y_future = np.maximum(y_future, 0)  # no negative victims

    # Generate future dates
    last_date = monthly["month_ts"].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=projection_months,
        freq="MS"
    )

    color = COLORS[group]

    # Plot actual data
    ax.bar(monthly["month_ts"], y, width=20, color=color, alpha=0.6, label="Monthly victims")

    # Plot trend line over actual data
    ax.plot(monthly["month_ts"], trend_line, color=color, linewidth=2, linestyle="--", label="Trend")

    # Plot projection
    ax.plot(future_dates, y_future, color="gray", linewidth=2, linestyle=":", marker="o", markersize=4, label="Projection")

    # Shade projection area
    ax.axvspan(future_dates[0], future_dates[-1], alpha=0.08, color="gray", label="Projection window")

    # Trend direction label
    direction = "+ Increasing" if slope > 0.5 else ("- Decreasing" if slope < -0.5 else "~ Stable")
    ax.set_title(f"{group.upper()}  |  {direction}  |  R²={r_value ** 2:.2f}", fontsize=10, fontweight="bold", pad=8)

    #ax.set_xlabel("Month")
    ax.set_ylabel("Victim Count")
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=55, ha="right",fontsize=7)
    for ann_date, ann_label, ann_y in ANNOTATIONS.get(group, []):
        ann_ts = pd.Timestamp(ann_date)

        # Only annotate if the date falls within the group's chart range
        if ann_ts >= monthly["month_ts"].min() and ann_ts <= monthly["month_ts"].max():
            ax.annotate(
                ann_label,
                xy=(ann_ts, ann_y * 0.6),  # arrow tip points here
                xytext=(ann_ts, ann_y),  # label sits here
                fontsize=6,
                color="black",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    color="black",
                    lw=0.8
                ),
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor="gray",
                    alpha=0.8
                )
            )

    ax.legend(fontsize=7, loc="upper left")
    ax.grid(axis="y", alpha=0.3)

axes[5].set_visible(True)
axes[5].axis("off")  # hide axes lines and ticks

explanation_text = (
    "Qualitative Case Annotations\n"
    "─────────────────────────────\n"
    "Labeled arrows on each chart mark\n"
    "months where a specific company was\n"
    "confirmed as a victim by that group.\n\n"
    "These companies were identified through\n"
    "cross-referencing ransomware.live victim\n"
    "data with public cybersecurity reporting\n"
    "(Halcyon, BleepingComputer, RedPacket).\n\n"
    "Companies appearing on multiple group\n"
    "charts indicate cross-group targeting —\n"
    "where two or more ransomware groups\n"
    "claimed the same victim, suggesting\n"
    "data resale or independent exploitation\n"
    "of the same vulnerabilities.\n\n"
)

axes[5].text(
    0.05, 1,
    explanation_text,
    transform=axes[5].transAxes,
    fontsize=11,
    verticalalignment="top",
    horizontalalignment="left",
    family="monospace",
    bbox=dict(
        boxstyle="round,pad=0.7",
        facecolor="orange",
        edgecolor="gray",
        linewidth=1.2,
        alpha=0.95
    )
)


plt.tight_layout(rect=[0, 0, 1, 0.96], h_pad=5.0, w_pad=3.0)
plt.savefig("victim_trend_projection.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved to victim_trend_projection.png")

