"""
Reuters Institute Digital News Report — Italy 2021-2026
Builds CSV datasets and generates charts for Substack article.

Data sources: extracted markdown files in ../extracted/
All values drawn directly from the Italy country sections.
Where a value is interpolated from chart graphics (PDF layout), it is marked.
"""

import csv
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

BASE = Path(__file__).parent
OUT_CSV = BASE / "csv"
OUT_IMG = BASE / "charts"
OUT_CSV.mkdir(exist_ok=True)
OUT_IMG.mkdir(exist_ok=True)

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

# ── PALETTE ──────────────────────────────────────────────────────────────────
C = {
    "trust":     "#C0392B",
    "print":     "#884EA0",
    "pay":       "#2471A3",
    "share":     "#1ABC9C",
    "avoidance": "#E67E22",
    "facebook":  "#3B5998",
    "instagram": "#C13584",
    "whatsapp":  "#25D366",
    "youtube":   "#FF0000",
    "tiktok":    "#010101",
    "telegram":  "#0088CC",
    "tv":        "#F39C12",
    "online":    "#2ECC71",
    "social":    "#E74C3C",
    "rsf":       "#922B21",
    "ai":        "#5D6D7E",
    "podcast":   "#76448A",
}

FONT = {"family": "sans-serif", "size": 11}
matplotlib.rc("font", **FONT)

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATASETS
# ─────────────────────────────────────────────────────────────────────────────

# Overall trust in news (% "trust most news most of the time")
# Source: Italy section, "OVERALL TRUST" label — confirmed in report text each year
trust = {
    2021: 40,   # Explicitly "+11pp" recovery; text states "40% (+11)" = 40% overall
    2022: 35,   # From longitudinal chart shown in 2023 report; described as "declined, particularly low"
    2023: 34,   # Explicitly stated "34%"
    2024: 34,   # Explicitly stated "34%"
    2025: 36,   # Explicitly stated "36%"
    2026: 32,   # Explicitly stated "32% (-4)"
}

# Print newspaper weekly reach
# Source: confirmed in CHANGING MEDIA text each year
print_reach = {
    2021: 18,
    2022: 15,
    2023: 16,
    2024: 13,
    2025: 12,
    2026: 11,
}

# TV news weekly reach (% using TV for news at least once/week)
# Source: SOURCES OF NEWS chart — position 1 in the changing data block
# 2026 text: "down slightly but remains comparatively high" (-3pp from 2025)
# 2024 text: "has declined" — confirmed -4pp drop
# NOTE: these are chart-derived values; confirmed by text descriptions
tv_reach = {
    2021: 76,
    2022: 70,
    2023: 69,
    2024: 65,
    2025: 65,
    2026: 62,
}

# Any online (incl. social) news weekly reach
# Source: SOURCES OF NEWS chart — position 2 in the changing data block
online_reach = {
    2021: 75,
    2022: 75,
    2023: 70,
    2024: 69,
    2025: 68,
    2026: 69,
}

# Social media for news (weekly)
# Source: SOURCES OF NEWS chart — position 4 in the changing data block
# 2026 text: "After an 11pp fall since 2020, social media use for news is up 6pp"
# 2025 was 39%, +6pp = 45% in 2026 ✓
social_reach = {
    2021: 47,
    2022: 47,
    2023: 42,
    2024: 39,
    2025: 39,
    2026: 45,
}

# Pay for online news (% who paid in last year)
# Source: confirmed in each Italy section
pay = {
    2021: 13,
    2022: 12,
    2023: 12,
    2024: 10,
    2025: 9,
    2026: 8,  # "8% (-1)" confirmed in 2026 AVOID/PAY block
}

# Share news via social/messaging/email
# Source: "SHARE NEWS via social, messaging or email" — confirmed where present
share_news = {
    2021: 40,
    2022: 36,
    2023: 34,
    2024: None,  # Not found in extracted 2024 section
    2025: 26,
    2026: None,  # Not found in 2026 section (different layout)
}

# Podcast listening (monthly) — note: metric changed in 2025 to "news podcasts weekly"
podcast = {
    2021: 31,   # "31% listen to PODCASTS in the last month"
    2022: 29,
    2023: 30,
    2024: 32,
    2025: None, # Metric changed to news podcasts weekly (6%)
    2026: None,
}

# News podcasts weekly (different metric, from 2025)
news_podcast_weekly = {
    2025: 6,
    2026: 6,
}

# AI chatbots for news (weekly) — new indicator
ai_chatbot = {
    2025: 4,
    2026: 6,
}

# Social media platforms for news (% used for news in last week)
platforms = {
    "Facebook":  {2021: 50, 2022: 45, 2023: 44, 2024: 37, 2025: 36, 2026: 44},
    "Instagram": {2021: 15, 2022: 18, 2023: 20, 2024: 20, 2025: 22, 2026: 31},
    "WhatsApp":  {2021: 30, 2022: 26, 2023: 27, 2024: 25, 2025: 21, 2026: 29},
    "YouTube":   {2021: 20, 2022: 21, 2023: 19, 2024: 20, 2025: 20, 2026: 21},
    "TikTok":    {2021: None, 2022: None, 2023: 8, 2024: 9, 2025: 10, 2026: 11},
    "Telegram":  {2021: 7, 2022: 9, 2023: 9, 2024: 8, 2025: 6, 2026: 7},
    "Twitter/X": {2021: 8, 2022: 8, 2023: None, 2024: None, 2025: None, 2026: None},
}

# Press Freedom Index (RSF) — rank and score
# Source: confirmed in Italy section from 2023 onward
press_freedom = {
    2023: {"rank": 41, "score": 72.05},
    2024: {"rank": 46, "score": 69.8},
    2025: {"rank": 49, "score": 68.01},
    2026: {"rank": 56, "score": 65.16},
}

# Brand trust (% "trust" = scored 6-10 on 10-point scale)
# Source: confirmed brand trust tables in Italy sections
brand_trust = {
    "ANSA":                     {2023: 78, 2024: 75, 2025: 74, 2026: 74},
    "SkyTG24":                  {2023: 71, 2024: 69, 2025: 67, 2026: 64},
    "Il Sole 24 Ore":           {2023: 69, 2024: 67, 2025: 67, 2026: 64},
    "Regional/local newspaper": {2023: 66, 2024: 60, 2025: 60, 2026: 60},
    "RAI":                      {2023: 63, 2024: 58, 2025: 58, 2026: 56},
    "Tg La7":                   {2023: 63, 2024: 62, 2025: 61, 2026: 58},
    "Il Corriere della Sera":   {2023: 63, 2024: 61, 2025: 60, 2026: 59},
    "La Repubblica":            {2023: 59, 2024: 58, 2025: 55, 2026: 55},
    "La Stampa":                {2023: 57, 2024: 54, 2025: 54, 2026: 54},
    "Mediaset News":            {2023: 58, 2024: 58, 2025: 57, 2026: 54},
    "Il Fatto Quotidiano":      {2023: 55, 2024: 53, 2025: 52, 2026: 54},
    "Il Giornale":              {2023: 51, 2024: 46, 2025: 46, 2026: 46},
    "IlPost.it":                {2023: None, 2024: 42, 2025: 44, 2026: 44},
    "Libero Quotidiano":        {2023: 47, 2024: 43, 2025: 44, 2026: 41},
    "Fanpage":                  {2023: 42, 2024: 42, 2025: 43, 2026: 41},
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. WRITE CSVs
# ─────────────────────────────────────────────────────────────────────────────

def write_csv(name, headers, rows):
    p = OUT_CSV / f"{name}.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  CSV → {p.name}")

# Main indicators
write_csv("indicators_over_time",
    ["year", "trust", "print_reach", "tv_reach", "online_reach", "social_reach", "pay", "share_news"],
    [[y, trust[y], print_reach[y], tv_reach[y], online_reach[y], social_reach[y], pay[y], share_news.get(y)] for y in YEARS]
)

# Platforms
platform_headers = ["year"] + list(platforms.keys())
platform_rows = [[y] + [platforms[p].get(y) for p in platforms] for y in YEARS]
write_csv("platforms_for_news", platform_headers, platform_rows)

# Press freedom
write_csv("press_freedom",
    ["year", "rank", "score"],
    [[y, press_freedom[y]["rank"], press_freedom[y]["score"]] for y in [2023,2024,2025,2026]]
)

# Brand trust
brand_headers = ["brand", "2023", "2024", "2025", "2026"]
brand_rows = [[b, brand_trust[b].get(2023), brand_trust[b].get(2024), brand_trust[b].get(2025), brand_trust[b].get(2026)]
              for b in brand_trust]
write_csv("brand_trust", brand_headers, brand_rows)

print("CSVs done.\n")

# ─────────────────────────────────────────────────────────────────────────────
# 3. CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def save(fig, name):
    p = OUT_IMG / f"{name}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Chart → {p.name}")


# ── CHART 1: Trust + Print + Pay — three declining lines ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(YEARS, [trust[y] for y in YEARS], "o-", color=C["trust"], lw=2.5, ms=7, label="Fiducia nelle notizie")
ax.plot(YEARS, [print_reach[y] for y in YEARS], "s--", color=C["print"], lw=2, ms=6, label="Stampa cartacea (reach settimanale)")
ax.plot(YEARS, [pay[y] for y in YEARS], "^-.", color=C["pay"], lw=2, ms=6, label="Paga per notizie online")

for y in YEARS:
    ax.annotate(f"{trust[y]}%", (y, trust[y]), textcoords="offset points", xytext=(0,9), ha="center", color=C["trust"], fontsize=9, fontweight="bold")
    ax.annotate(f"{print_reach[y]}%", (y, print_reach[y]), textcoords="offset points", xytext=(0,-14), ha="center", color=C["print"], fontsize=9)
    ax.annotate(f"{pay[y]}%", (y, pay[y]), textcoords="offset points", xytext=(0,9), ha="center", color=C["pay"], fontsize=9)

ax.set_xlim(2020.5, 2026.5)
ax.set_ylim(0, 55)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Fiducia, stampa e pagamento per le notizie (2021–2026)", fontsize=13, fontweight="bold", pad=14)
ax.legend(loc="upper right", fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021–2026", ha="center", fontsize=8, color="gray")
save(fig, "01_trust_print_pay")


# ── CHART 2: Sources of news — TV, Online, Social, Print ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(YEARS, [tv_reach[y] for y in YEARS],     "o-",  color=C["tv"],     lw=2.5, ms=7, label="TV")
ax.plot(YEARS, [online_reach[y] for y in YEARS], "s-",  color=C["online"], lw=2.5, ms=7, label="Qualsiasi online (incl. social)")
ax.plot(YEARS, [social_reach[y] for y in YEARS], "^--", color=C["social"], lw=2,   ms=6, label="Social media")
ax.plot(YEARS, [print_reach[y] for y in YEARS],  "D-.", color=C["print"],  lw=2,   ms=6, label="Stampa cartacea")

for y in YEARS:
    ax.annotate(f"{tv_reach[y]}%",     (y, tv_reach[y]),     textcoords="offset points", xytext=(0,9),   ha="center", color=C["tv"],     fontsize=8)
    ax.annotate(f"{online_reach[y]}%", (y, online_reach[y]), textcoords="offset points", xytext=(0,-14), ha="center", color=C["online"], fontsize=8)
    ax.annotate(f"{social_reach[y]}%", (y, social_reach[y]), textcoords="offset points", xytext=(0,9),   ha="center", color=C["social"], fontsize=8)
    ax.annotate(f"{print_reach[y]}%",  (y, print_reach[y]),  textcoords="offset points", xytext=(0,-14), ha="center", color=C["print"],  fontsize=8)

ax.set_xlim(2020.5, 2026.5)
ax.set_ylim(0, 90)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Reach settimanale per fonte di notizie (2021–2026)", fontsize=13, fontweight="bold", pad=14)
ax.legend(loc="upper right", fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
ax.annotate("* Dati TV e online derivati da chart PDF;\n  confermati da descrizioni testuali",
            xy=(0.01, 0.03), xycoords="axes fraction", fontsize=7.5, color="gray")
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021–2026", ha="center", fontsize=8, color="gray")
save(fig, "02_sources_of_news")


# ── CHART 3: Social platforms (main 4) ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))
main_platforms = ["Facebook", "Instagram", "WhatsApp", "YouTube"]
pcolors = [C["facebook"], C["instagram"], C["whatsapp"], C["youtube"]]
markers = ["o", "s", "^", "D"]

for plat, col, mk in zip(main_platforms, pcolors, markers):
    vals = [platforms[plat].get(y) for y in YEARS]
    ax.plot(YEARS, vals, f"{mk}-", color=col, lw=2.5, ms=7, label=plat)
    for y, v in zip(YEARS, vals):
        if v is not None:
            ax.annotate(f"{v}%", (y, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8, color=col)

ax.set_xlim(2020.5, 2026.5)
ax.set_ylim(0, 60)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Uso delle principali piattaforme per le notizie (2021–2026)", fontsize=13, fontweight="bold", pad=14)
ax.legend(loc="upper right", fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)

# Annotate the 2026 rebound
ax.annotate("Rimbalzo 2026\n+8pp Facebook\n+9pp Instagram\n+8pp WhatsApp",
            xy=(2026, 44), xytext=(2024.8, 50),
            fontsize=8, color="#555",
            arrowprops=dict(arrowstyle="->", color="#aaa", lw=1))
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021–2026", ha="center", fontsize=8, color="gray")
save(fig, "03_social_platforms")


# ── CHART 4: Emerging platforms — TikTok, Telegram, Twitter/X ────────────────
fig, ax = plt.subplots(figsize=(10, 4.5))
emerg = ["TikTok", "Telegram", "Twitter/X"]
ecolors = [C["tiktok"], C["telegram"], "#1DA1F2"]
emarkers = ["o", "s", "^"]

for plat, col, mk in zip(emerg, ecolors, emarkers):
    ys = [y for y in YEARS if platforms[plat].get(y) is not None]
    vs = [platforms[plat][y] for y in ys]
    ax.plot(ys, vs, f"{mk}-", color=col, lw=2.5, ms=7, label=plat)
    for y, v in zip(ys, vs):
        ax.annotate(f"{v}%", (y, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8.5, color=col)

ax.axvspan(2025.5, 2026.5, alpha=0.05, color="gray", label="Twitter/X scompare dalla top 6")
ax.set_xlim(2020.5, 2026.5)
ax.set_ylim(0, 18)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Piattaforme emergenti per le notizie (2021–2026)", fontsize=13, fontweight="bold", pad=14)
ax.legend(loc="upper left", fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
ax.annotate("Twitter/X esce dalla top 6\ndei social per le notizie",
            xy=(2022.3, 8), xytext=(2021.2, 13),
            fontsize=8, color="#1DA1F2",
            arrowprops=dict(arrowstyle="->", color="#aaa", lw=1))
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021–2026", ha="center", fontsize=8, color="gray")
save(fig, "04_emerging_platforms")


# ── CHART 5: Press Freedom Index ─────────────────────────────────────────────
pf_years = [2023, 2024, 2025, 2026]
pf_ranks = [press_freedom[y]["rank"] for y in pf_years]
pf_scores = [press_freedom[y]["score"] for y in pf_years]

fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax2 = ax1.twinx()

bars = ax1.bar(pf_years, pf_ranks, color=C["rsf"], alpha=0.75, width=0.4, label="Ranking RSF (più basso = meglio)")
ax2.plot(pf_years, pf_scores, "o-", color="#E74C3C", lw=2.5, ms=8, label="Score RSF (più alto = meglio)")

for y, r, s in zip(pf_years, pf_ranks, pf_scores):
    ax1.annotate(f"{r}°", (y, r), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=11, fontweight="bold", color=C["rsf"])
    ax2.annotate(f"{s}", (y, s), textcoords="offset points", xytext=(12, 0), ha="left", fontsize=9, color="#E74C3C")

ax1.set_ylim(0, 75)
ax1.invert_yaxis()  # Lower rank = worse, show visually as going down
ax1.set_ylabel("Posizione (1=meglio)", color=C["rsf"])
ax2.set_ylim(60, 78)
ax2.set_ylabel("Score RSF", color="#E74C3C")
ax1.set_xticks(pf_years)
ax1.set_title("Italia: Libertà di stampa (RSF) 2023–2026", fontsize=13, fontweight="bold", pad=14)
ax1.spines[["top"]].set_visible(False)
ax2.spines[["top"]].set_visible(False)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=9)
fig.text(0.5, -0.03, "Fonte: Reporters Without Borders, via Reuters Institute Digital News Report 2023–2026", ha="center", fontsize=8, color="gray")
save(fig, "05_press_freedom")


# ── CHART 6: Brand trust heatmap (2023–2026) ─────────────────────────────────
brands_sorted = sorted(brand_trust.keys(), key=lambda b: brand_trust[b].get(2026, 0) or 0, reverse=True)
bt_years = [2023, 2024, 2025, 2026]
matrix = []
for b in brands_sorted:
    row = []
    for y in bt_years:
        v = brand_trust[b].get(y)
        row.append(v if v is not None else np.nan)
    matrix.append(row)

matrix = np.array(matrix, dtype=float)

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(matrix, cmap="RdYlGn", vmin=35, vmax=82, aspect="auto")

ax.set_xticks(range(len(bt_years)))
ax.set_xticklabels(bt_years, fontsize=11)
ax.set_yticks(range(len(brands_sorted)))
ax.set_yticklabels(brands_sorted, fontsize=10)

for i in range(len(brands_sorted)):
    for j in range(len(bt_years)):
        v = matrix[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{int(v)}%", ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color="white" if v < 52 else "black")

plt.colorbar(im, ax=ax, label="% che si fida del brand", shrink=0.6)
ax.set_title("Italia: Fiducia nei brand giornalistici (2023–2026)", fontsize=13, fontweight="bold", pad=14)
fig.text(0.5, -0.01, "Fonte: Reuters Institute Digital News Report, sezione Italia 2023–2026", ha="center", fontsize=8, color="gray")
save(fig, "06_brand_trust_heatmap")


# ── CHART 7: Share news + Podcast (general) — comportamento attivo ────────────
fig, ax = plt.subplots(figsize=(10, 4.5))

share_y = [y for y in YEARS if share_news.get(y) is not None]
share_v = [share_news[y] for y in share_y]
pod_y = [y for y in YEARS if podcast.get(y) is not None]
pod_v = [podcast[y] for y in pod_y]

ax.plot(share_y, share_v, "o-", color=C["share"], lw=2.5, ms=7, label="Condivide notizie via social/messag.")
ax.plot(pod_y, pod_v, "s--", color=C["podcast"], lw=2.5, ms=7, label="Ascolta podcast (mensile)")

for y, v in zip(share_y, share_v):
    ax.annotate(f"{v}%", (y, v), textcoords="offset points", xytext=(0, 10), ha="center", color=C["share"], fontsize=9, fontweight="bold")
for y, v in zip(pod_y, pod_v):
    ax.annotate(f"{v}%", (y, v), textcoords="offset points", xytext=(0, -14), ha="center", color=C["podcast"], fontsize=9)

ax.set_xlim(2020.5, 2026.5)
ax.set_ylim(0, 55)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Comportamento attivo — condivisione e podcast (2021–2025)", fontsize=13, fontweight="bold", pad=14)
ax.legend(loc="upper right", fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
ax.annotate("2024: dato share\nnon disponibile", xy=(2024, 30), fontsize=8, color="gray", ha="center")
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021–2025", ha="center", fontsize=8, color="gray")
save(fig, "07_share_and_podcast")


# ── CHART 8: 2021 vs 2026 — snapshot comparativo a barre ─────────────────────
categories = ["Fiducia\nnelle notizie", "Stampa\ncartacea", "Facebook\nper news", "Instagram\nper news",
              "WhatsApp\nper news", "YouTube\nper news", "Social media\nper news", "Paga online"]
vals_2021 = [trust[2021], print_reach[2021], platforms["Facebook"][2021], platforms["Instagram"][2021],
             platforms["WhatsApp"][2021], platforms["YouTube"][2021], social_reach[2021], pay[2021]]
vals_2026 = [trust[2026], print_reach[2026], platforms["Facebook"][2026], platforms["Instagram"][2026],
             platforms["WhatsApp"][2026], platforms["YouTube"][2026], social_reach[2026], pay[2026]]

x = np.arange(len(categories))
w = 0.35

fig, ax = plt.subplots(figsize=(13, 5.5))
b1 = ax.bar(x - w/2, vals_2021, w, label="2021", color="#2C3E50", alpha=0.85)
b2 = ax.bar(x + w/2, vals_2026, w, label="2026", color="#E74C3C", alpha=0.85)

for bar in b1:
    h = bar.get_height()
    ax.annotate(f"{int(h)}%", xy=(bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, color="#2C3E50")
for bar in b2:
    h = bar.get_height()
    ax.annotate(f"{int(h)}%", xy=(bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, color="#E74C3C")

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9.5)
ax.set_ylim(0, 65)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Italia: Confronto 2021 vs 2026 — principali indicatori", fontsize=13, fontweight="bold", pad=14)
ax.legend(fontsize=11)
ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
fig.text(0.5, -0.03, "Fonte: Reuters Institute Digital News Report, sezione Italia 2021 e 2026", ha="center", fontsize=8, color="gray")
save(fig, "08_snapshot_2021_vs_2026")


print("\nTutti i grafici generati.")
