import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(BASE_DIR, "data", "raw_retail_sales.csv")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "cleaned_retail_sales.csv")
SQL_FILE = os.path.join(BASE_DIR, "sql", "sql_queries.sql")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# 1. Load Raw Data
df = pd.read_csv(RAW_CSV)
print(f"Raw dataset shape: {df.shape}")

# 2. Data Cleaning
df = df.drop_duplicates(subset=["Order_ID"]).copy()
df["Category"] = df["Category"].astype(str).str.strip()
df["Region"] = df["Region"].astype(str).str.strip()
df["Product_Name"] = df["Product_Name"].astype(str).str.strip()
df["Customer_Segment"] = df["Customer_Segment"].fillna("Consumer")
df["Discount"] = df["Discount"].fillna(0.0)

df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="mixed", dayfirst=True)
df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Order_Date"] = df["Order_Date"].dt.strftime("%Y-%m-%d")

df.to_csv(CLEAN_CSV, index=False)
print(f"Cleaned dataset shape: {df.shape}")

# 3. Run SQL Analysis via SQLite
conn = sqlite3.connect(":memory:")
df.to_sql("retail_sales", conn, index=False, if_exists="replace")

with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql_script = f.read()

queries = [q.strip() for q in sql_script.split(";") if q.strip()]
for idx, query in enumerate(queries, 1):
    print(f"\n--- SQL Query {idx} Result ---")
    res = pd.read_sql_query(query, conn)
    print(res.to_string(index=False))

conn.close()

# 4. Generate Individual Charts + 4-Panel Executive Dashboard PNG
plt.style.use("seaborn-v0_8-whitegrid")

monthly = df.groupby("Order_Month")[["Sales", "Profit"]].sum().reset_index()
cat_summary = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
reg_summary = df.groupby("Region")["Sales"].sum().sort_values(ascending=True)
seg_summary = df.groupby("Customer_Segment")["Sales"].sum().sort_values(ascending=False)

# Discount tier summary
def disc_tier(d):
    if d == 0:
        return "0% (No Disc)"
    elif d <= 0.15:
        return "1% - 15%"
    return "> 15%"

df["Discount_Tier"] = df["Discount"].apply(disc_tier)
disc_summary = df.groupby("Discount_Tier")[["Sales", "Profit"]].sum()
disc_summary["Margin_Pct"] = disc_summary["Profit"] * 100.0 / disc_summary["Sales"]
disc_summary = disc_summary.reindex(["0% (No Disc)", "1% - 15%", "> 15%"])

# Individual Chart 1: Monthly Trend
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["Order_Month"], monthly["Sales"], marker="o", linewidth=2.5, color="#1F4E78", label="Revenue")
ax.plot(monthly["Order_Month"], monthly["Profit"], marker="s", linewidth=2.5, color="#2E7D32", label="Profit")
ax.set_title("Monthly Revenue vs Profit Trend (2025)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=11)
ax.set_ylabel("Amount (INR)", fontsize=11)
plt.xticks(rotation=45)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "monthly_revenue_trend.png"), dpi=150)
plt.close()

# Individual Chart 2: Category Sales vs Profit
fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(cat_summary))
width = 0.35
ax.bar([i - width/2 for i in x], cat_summary["Sales"], width=width, color="#1F4E78", label="Total Sales")
ax.bar([i + width/2 for i in x], cat_summary["Profit"], width=width, color="#2E7D32", label="Total Profit")
ax.set_xticks(list(x))
ax.set_xticklabels(cat_summary.index, fontsize=11)
ax.set_title("Category-Wise Sales vs Profit", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Amount (INR)", fontsize=11)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "category_sales_vs_profit.png"), dpi=150)
plt.close()

# Individual Chart 3: Region Performance
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.barh(reg_summary.index, reg_summary.values, color="#2B6CB0")
ax.set_title("Total Sales by Region", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Total Sales (INR)", fontsize=11)
for bar in bars:
    val = bar.get_width()
    ax.text(val + max(reg_summary.values) * 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:,.0f}", va="center", fontsize=10)
ax.set_xlim(0, max(reg_summary.values) * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "region_performance.png"), dpi=150)
plt.close()

# Executive 4-Panel Dashboard PNG
fig = plt.figure(figsize=(16, 10), facecolor="#F8FAFC")
gs = gridspec.GridSpec(3, 2, height_ratios=[0.24, 1, 1], hspace=0.38, wspace=0.25)

# Top KPI Banner
ax_kpi = fig.add_subplot(gs[0, :])
ax_kpi.axis("off")
total_rev = df["Sales"].sum()
total_prof = df["Profit"].sum()
margin = total_prof * 100.0 / total_rev
aov = df["Sales"].mean()

ax_kpi.text(0.0, 0.98, "RETAIL SALES & PROFIT EXECUTIVE DASHBOARD (FY 2025)",
            fontsize=18, fontweight="bold", color="#0F172A", va="top")
kpi_cards = [
    ("Total Orders", f"{len(df):,}"),
    ("Total Revenue", f"INR {total_rev:,.0f}"),
    ("Total Profit", f"INR {total_prof:,.0f}"),
    ("Profit Margin", f"{margin:.2f}%"),
    ("Avg Order Value", f"INR {aov:,.0f}"),
]
for idx, (label, val) in enumerate(kpi_cards):
    xpos = 0.0 + idx * 0.205
    ax_kpi.text(xpos, 0.48, label, fontsize=10, color="#475569", fontweight="bold")
    ax_kpi.text(xpos, 0.14, val, fontsize=14, color="#1F4E78", fontweight="bold")

# Panel 1: Monthly Trend
ax1 = fig.add_subplot(gs[1, 0])
ax1.plot(monthly["Order_Month"], monthly["Sales"] / 1000, marker="o", color="#1F4E78", linewidth=2.2, label="Revenue (K)")
ax1.plot(monthly["Order_Month"], monthly["Profit"] / 1000, marker="s", color="#2E7D32", linewidth=2.2, label="Profit (K)")
ax1.set_title("Monthly Revenue & Profit Trend (in Thousands)", fontsize=12, fontweight="bold", color="#1E293B")
ax1.tick_params(axis="x", rotation=40, labelsize=9)
ax1.legend(frameon=True)

# Panel 2: Category Sales vs Profit
ax2 = fig.add_subplot(gs[1, 1])
cx = range(len(cat_summary))
ax2.bar([i - 0.18 for i in cx], cat_summary["Sales"] / 1000, width=0.36, color="#1F4E78", label="Sales (K)")
ax2.bar([i + 0.18 for i in cx], cat_summary["Profit"] / 1000, width=0.36, color="#2E7D32", label="Profit (K)")
ax2.set_xticks(list(cx))
ax2.set_xticklabels(cat_summary.index, fontsize=10)
ax2.set_title("Category Performance (Sales vs Profit in K)", fontsize=12, fontweight="bold", color="#1E293B")
ax2.legend(frameon=True)

# Panel 3: Discount Impact on Profit Margin
ax3 = fig.add_subplot(gs[2, 0])
colors_disc = ["#2E7D32" if v > 0 else "#C62828" for v in disc_summary["Margin_Pct"]]
bars3 = ax3.bar(disc_summary.index, disc_summary["Margin_Pct"], color=colors_disc, width=0.5)
ax3.axhline(0, color="#334155", linewidth=1)
ax3.set_title("Profit Margin (%) by Discount Tier", fontsize=12, fontweight="bold", color="#1E293B")
ax3.set_ylabel("Margin (%)", fontsize=10)
for b in bars3:
    h = b.get_height()
    va = "bottom" if h >= 0 else "top"
    offset = 0.6 if h >= 0 else -0.8
    ax3.text(b.get_x() + b.get_width()/2, h + offset, f"{h:.2f}%", ha="center", va=va, fontsize=10, fontweight="bold")
ax3.set_ylim(min(disc_summary["Margin_Pct"].min() - 4, -12), disc_summary["Margin_Pct"].max() + 4)

# Panel 4: Customer Segment Share & Region Sales
ax4 = fig.add_subplot(gs[2, 1])
bars4 = ax4.barh(seg_summary.index[::-1], seg_summary.values[::-1] / 1000, color=["#64748B", "#3B82F6", "#1F4E78"])
ax4.set_title("Revenue by Customer Segment (in Thousands)", fontsize=12, fontweight="bold", color="#1E293B")
ax4.set_xlabel("Revenue (INR K)", fontsize=10)
for b in bars4:
    w = b.get_width()
    ax4.text(w + 15, b.get_y() + b.get_height()/2, f"{w:,.1f}K", va="center", fontsize=10, fontweight="bold")
ax4.set_xlim(0, (seg_summary.max() / 1000) * 1.18)

fig.subplots_adjust(left=0.06, right=0.97, top=0.95, bottom=0.08)
plt.savefig(os.path.join(CHARTS_DIR, "executive_dashboard.png"), dpi=160, facecolor=fig.get_facecolor())
plt.close()

print("\nAll charts including executive_dashboard.png saved successfully.")
