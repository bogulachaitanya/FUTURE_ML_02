import pandas as pd
import matplotlib.pyplot as plt
import os

report_file = "reports/ticket_report.csv"

if not os.path.exists(report_file):
    print("No reports available yet.")
    exit()

df = pd.read_csv(report_file)

# Category Chart
category_counts = df["Category"].value_counts()

plt.figure(figsize=(6,4))
category_counts.plot(kind="bar")

plt.title("Live Category Distribution")
plt.ylabel("Count")

plt.tight_layout()

plt.savefig("static/category_chart.png")

plt.close()

# Priority Chart
priority_counts = df["Priority"].value_counts()

plt.figure(figsize=(6,4))
priority_counts.plot(kind="bar")

plt.title("Live Priority Distribution")
plt.ylabel("Count")

plt.tight_layout()

plt.savefig("static/priority_chart.png")

plt.close()

print("Live Charts Updated Successfully")

# Trend Chart

if "Timestamp" in df.columns:

    df["Date"] = pd.to_datetime(
        df["Timestamp"]
    ).dt.date

    trend = df.groupby("Date").size()

    plt.figure(figsize=(6,4))

    trend.plot(kind="line", marker="o")

    plt.title("Ticket Activity Trend")

    plt.ylabel("Tickets")

    plt.tight_layout()

    plt.savefig(
        "static/trend_chart.png"
    )

    plt.close()