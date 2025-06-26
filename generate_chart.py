#!/usr/bin/env python3
# PR‑tracker: generates a combo chart from the collected PR data.
# deps: pandas, matplotlib, numpy

from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import re
import json
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path("templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
env.filters["comma"] = lambda v: f"{int(v):,}" if isinstance(v, (int, float)) else v

AGENTS = [
    {
        "key": "copilot",
        "display": "Copilot",
        "long_name": "GitHub Copilot",
        "color": "#2563eb",
        "info_url": "https://docs.github.com/en/copilot/using-github-copilot/coding-agent/using-copilot-to-work-on-an-issue",
        "total_query_url": "https://github.com/search?q=is:pr+head:copilot/&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests",
    },
    {
        "key": "codex",
        "display": "Codex",
        "long_name": "OpenAI Codex",
        "color": "#dc2626",
        "info_url": "https://openai.com/index/introducing-codex/",
        "total_query_url": "https://github.com/search?q=is:pr+head:codex/&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests",
    },
    {
        "key": "cursor",
        "display": "Cursor",
        "long_name": "Cursor Agents",
        "color": "#7c3aed",
        "info_url": "https://docs.cursor.com/background-agent",
        "total_query_url": "https://github.com/search?q=is:pr+head:cursor/&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests",
    },
    {
        "key": "devin",
        "display": "Devin",
        "long_name": "Devin",
        "color": "#059669",
        "info_url": "https://devin.ai/pricing",
        "total_query_url": "https://github.com/search?q=is:pr+author:devin-ai-integration[bot]&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+author:devin-ai-integration[bot]+is:merged&type=pullrequests",
    },
    {
        "key": "codegen",
        "display": "Codegen",
        "long_name": "Codegen",
        "color": "#d97706",
        "info_url": "https://codegen.com/",
        "total_query_url": "https://github.com/search?q=is:pr+author:codegen-sh[bot]&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+author:codegen-sh[bot]+is:merged&type=pullrequests",
    },
    {
        "key": "cosine",
        "display": "Cosine",
        "long_name": "Cosine Agent",
        "color": "#0ea5e9",
        "info_url": "https://cosine.dev/",
        "total_query_url": "https://github.com/search?q=is:pr+head:cosine/&type=pullrequests",
        "merged_query_url": "https://github.com/search?q=is:pr+head:cosine/+is:merged&type=pullrequests",
    },
]


def build_stats(latest, df=None):
    stats = {}

    # Get real data for each agent
    for agent in AGENTS:
        key = agent["key"]
        total = int(latest[f"{key}_total"])
        merged = int(latest[f"{key}_merged"])
        rate = (merged / total * 100) if total > 0 else 0

        # Simple, meaningful stats only
        stats[key] = {
            "total": total,
            "merged": merged,
            "rate": rate,
        }
    return stats


def generate_chart(csv_file=None):
    # Default to data.csv if no file specified
    if csv_file is None:
        csv_file = Path("data.csv")

    # Ensure file exists
    if not csv_file.exists():
        print(f"Error: {csv_file} not found.")
        print("Run collect_data.py first to collect data.")
        return False

    # Create chart
    df = pd.read_csv(csv_file)
    # Fix timestamp format - replace special dash characters with regular hyphens
    df["timestamp"] = df["timestamp"].str.replace("‑", "-")
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Check if data exists
    if len(df) == 0:
        print("Error: No data found in CSV file.")
        return False

    # Limit to 8 data points spread across the entire dataset to avoid chart getting too busy
    total_points = len(df)
    if total_points > 8:
        # Create evenly spaced indices across the entire dataset
        indices = np.linspace(0, total_points - 1, num=8, dtype=int)
        df = df.iloc[indices]
        print(
            f"Limited chart to 8 data points evenly distributed across {total_points} total points."
        )

    # Calculate percentages with safety checks
    df["copilot_percentage"] = df.apply(
        lambda row: (
            (row["copilot_merged"] / row["copilot_total"] * 100)
            if row["copilot_total"] > 0
            else 0
        ),
        axis=1,
    )
    df["codex_percentage"] = df.apply(
        lambda row: (
            (row["codex_merged"] / row["codex_total"] * 100)
            if row["codex_total"] > 0
            else 0
        ),
        axis=1,
    )
    df["cursor_percentage"] = df.apply(
        lambda row: (
            (row["cursor_merged"] / row["cursor_total"] * 100)
            if row["cursor_total"] > 0
            else 0
        ),
        axis=1,
    )
    df["devin_percentage"] = df.apply(
        lambda row: (
            (row["devin_merged"] / row["devin_total"] * 100)
            if row["devin_total"] > 0
            else 0
        ),
        axis=1,
    )
    df["codegen_percentage"] = df.apply(
        lambda row: (
            (row["codegen_merged"] / row["codegen_total"] * 100)
            if row["codegen_total"] > 0
            else 0
        ),
        axis=1,
    )
    df["cosine_percentage"] = df.apply(
        lambda row: (
            (row["cosine_merged"] / row["cosine_total"] * 100)
            if row.get("cosine_total", 0) > 0
            else 0
        ),
        axis=1,
    )

    # Adjust chart size based on data points, adding extra space for legends
    num_points = len(df)
    if num_points <= 3:
        fig_width = max(12, num_points * 4)  # Increased from 10 to 12
        fig_height = 8  # Increased from 6 to 8
    else:
        fig_width = 16  # Increased from 14 to 16
        fig_height = 10  # Increased from 8 to 10

    # Create the combination chart
    fig, ax1 = plt.subplots(figsize=(fig_width, fig_height))
    ax2 = ax1.twinx()

    # Prepare data
    x = np.arange(len(df))
    # Adjust bar width based on number of data points (5 groups now)
    width = min(0.16, 0.8 / max(1, num_points * 0.6))

    # Bar charts for totals and merged
    bars_copilot_total = ax1.bar(
        x - 2 * width,
        df["copilot_total"],
        width,
        label="Copilot Total",
        alpha=0.7,
        color="#93c5fd",
    )
    bars_copilot_merged = ax1.bar(
        x - 2 * width,
        df["copilot_merged"],
        width,
        label="Copilot Merged",
        alpha=1.0,
        color="#2563eb",
    )

    bars_codex_total = ax1.bar(
        x - 1 * width,
        df["codex_total"],
        width,
        label="Codex Total",
        alpha=0.7,
        color="#fca5a5",
    )
    bars_codex_merged = ax1.bar(
        x - 1 * width,
        df["codex_merged"],
        width,
        label="Codex Merged",
        alpha=1.0,
        color="#dc2626",
    )

    bars_cursor_total = ax1.bar(
        x + 0 * width,
        df["cursor_total"],
        width,
        label="Cursor Total",
        alpha=0.7,
        color="#c4b5fd",
    )
    bars_cursor_merged = ax1.bar(
        x + 0 * width,
        df["cursor_merged"],
        width,
        label="Cursor Merged",
        alpha=1.0,
        color="#7c3aed",
    )

    bars_devin_total = ax1.bar(
        x + 1 * width,
        df["devin_total"],
        width,
        label="Devin Total",
        alpha=0.7,
        color="#86efac",
    )
    bars_devin_merged = ax1.bar(
        x + 1 * width,
        df["devin_merged"],
        width,
        label="Devin Merged",
        alpha=1.0,
        color="#059669",
    )

    bars_codegen_total = ax1.bar(
        x + 2 * width,
        df["codegen_total"],
        width,
        label="Codegen Total",
        alpha=0.7,
        color="#fed7aa",
    )
    bars_codegen_merged = ax1.bar(
        x + 2 * width,
        df["codegen_merged"],
        width,
        label="Codegen Merged",
        alpha=1.0,
        color="#d97706",
    )

    # Line charts for percentages (on secondary y-axis)
    line_copilot = ax2.plot(
        x,
        df["copilot_percentage"],
        "o-",
        color="#1d4ed8",
        linewidth=3,
        markersize=10,
        label="Copilot Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#1d4ed8",
    )

    line_codex = ax2.plot(
        x,
        df["codex_percentage"],
        "s-",
        color="#b91c1c",
        linewidth=3,
        markersize=10,
        label="Codex Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#b91c1c",
    )

    line_cursor = ax2.plot(
        x,
        df["cursor_percentage"],
        "d-",
        color="#6d28d9",
        linewidth=3,
        markersize=10,
        label="Cursor Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#6d28d9",
    )

    line_devin = ax2.plot(
        x,
        df["devin_percentage"],
        "^-",
        color="#047857",
        linewidth=3,
        markersize=10,
        label="Devin Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#047857",
    )

    line_codegen = ax2.plot(
        x,
        df["codegen_percentage"],
        "v-",
        color="#b45309",
        linewidth=3,
        markersize=10,
        label="Codegen Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#b45309",
    )

    # Customize the chart
    ax1.set_xlabel("Data Points", fontsize=12, fontweight="bold")
    ax1.set_ylabel(
        "PR Counts (Total & Merged)", fontsize=12, fontweight="bold", color="black"
    )
    ax2.set_ylabel(
        "Merge Success Rate (%)", fontsize=12, fontweight="bold", color="black"
    )

    title = "PR Analytics: Volume vs Success Rate Comparison"
    ax1.set_title(title, fontsize=16, fontweight="bold", pad=20)

    # Set x-axis labels with timestamps
    timestamps = df["timestamp"].dt.strftime("%m-%d %H:%M")
    ax1.set_xticks(x)
    ax1.set_xticklabels(timestamps, rotation=45)

    # Add legends - move name labels to top left, success % labels to bottom right
    # Position legends further outside with more padding
    legend1 = ax1.legend(loc="upper left", bbox_to_anchor=(-0.15, 1.15))
    legend2 = ax2.legend(loc="lower right", bbox_to_anchor=(1.15, -0.15))

    # Add grid
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Set percentage axis range
    ax2.set_ylim(0, 100)

    # Add value labels on bars (with safety checks)
    def add_value_labels(ax, bars, format_str="{:.0f}"):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                # Ensure the label fits within reasonable bounds
                label_text = format_str.format(height)
                if len(label_text) > 10:  # Truncate very long numbers
                    if height >= 1000:
                        label_text = f"{height/1000:.1f}k"
                    elif height >= 1000000:
                        label_text = f"{height/1000000:.1f}M"

                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    label_text,
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="normal",
                    color="black",
                )

    add_value_labels(ax1, bars_copilot_total)
    add_value_labels(ax1, bars_copilot_merged)
    add_value_labels(ax1, bars_codex_total)
    add_value_labels(ax1, bars_codex_merged)
    add_value_labels(ax1, bars_cursor_total)
    add_value_labels(ax1, bars_cursor_merged)
    add_value_labels(ax1, bars_devin_total)
    add_value_labels(ax1, bars_devin_merged)
    add_value_labels(ax1, bars_codegen_total)
    add_value_labels(ax1, bars_codegen_merged)

    # Add percentage labels on line points (with validation and skip 0.0%)
    for i, (cop_pct, cod_pct, cur_pct, dev_pct, cg_pct) in enumerate(
        zip(
            df["copilot_percentage"],
            df["codex_percentage"],
            df["cursor_percentage"],
            df["devin_percentage"],
            df["codegen_percentage"],
        )
    ):
        # Only add labels if percentages are valid numbers and not 0.0%
        if (
            pd.notna(cop_pct)
            and pd.notna(cod_pct)
            and pd.notna(cur_pct)
            and pd.notna(dev_pct)
            and pd.notna(cg_pct)
        ):
            if cop_pct > 0.0:
                ax2.annotate(
                    f"{cop_pct:.1f}%",
                    (i, cop_pct),
                    textcoords="offset points",
                    xytext=(0, 15),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#1d4ed8",
                )
            if cod_pct > 0.0:
                ax2.annotate(
                    f"{cod_pct:.1f}%",
                    (i, cod_pct),
                    textcoords="offset points",
                    xytext=(0, -20),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#b91c1c",
                )
            if cur_pct > 0.0:
                ax2.annotate(
                    f"{cur_pct:.1f}%",
                    (i, cur_pct),
                    textcoords="offset points",
                    xytext=(0, -35),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#6d28d9",
                )
            if dev_pct > 0.0:
                ax2.annotate(
                    f"{dev_pct:.1f}%",
                    (i, dev_pct),
                    textcoords="offset points",
                    xytext=(0, -50),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#047857",
                )
            if cg_pct > 0.0:
                ax2.annotate(
                    f"{cg_pct:.1f}%",
                    (i, cg_pct),
                    textcoords="offset points",
                    xytext=(0, -65),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#b45309",
                )

    plt.tight_layout(pad=6.0)

    # Adjust subplot parameters to ensure legends fit entirely outside the chart
    plt.subplots_adjust(left=0.2, right=0.85, top=0.85, bottom=0.2)

    # Save chart to docs directory (single location for both README and GitHub Pages)
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)  # Ensure docs directory exists
    chart_file = docs_dir / "chart.png"
    dpi = 150 if num_points <= 5 else 300
    fig.savefig(chart_file, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"Chart generated: {chart_file}")

    # Export chart data as JSON for interactive chart
    export_chart_data_json(df)

    # Update the README with latest statistics
    update_readme(df)

    # Update the GitHub Pages with latest statistics
    update_github_pages(df)

    return True


def export_chart_data_json(df):
    """Export chart data as JSON for interactive JavaScript chart"""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    # Prepare data for Chart.js
    chart_data = {"labels": [], "datasets": []}

    # Format timestamps for labels
    for _, row in df.iterrows():
        timestamp = row["timestamp"]
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        chart_data["labels"].append(timestamp.strftime("%m/%d %H:%M"))

    # Color scheme matching the Python chart - elegant professional colors
    colors = {
        "copilot": {"total": "#93c5fd", "merged": "#2563eb", "line": "#1d4ed8"},
        "codex": {"total": "#fca5a5", "merged": "#dc2626", "line": "#b91c1c"},
        "cursor": {"total": "#c4b5fd", "merged": "#7c3aed", "line": "#6d28d9"},
        "devin": {"total": "#86efac", "merged": "#059669", "line": "#047857"},
        "codegen": {"total": "#fed7aa", "merged": "#d97706", "line": "#b45309"},
        "cosine": {
            "total": "#ffb3ff",   # light magenta (for total bars)
            "merged": "#FF00FF",  # strong magenta (for merged bars)
            "line": "#c800c8",    # darker magenta (for line)
        },
    }

    # Add bar datasets for totals and merged PRs
    for agent in ["copilot", "codex", "cursor", "devin", "codegen", "cosine"]:
        # Process data to replace leading zeros with None (null in JSON)
        total_data = df.get(f"{agent}_total", pd.Series([0]*len(df))).tolist()
        merged_data = df.get(f"{agent}_merged", pd.Series([0]*len(df))).tolist()
        percentage_data = df.get(f"{agent}_percentage", pd.Series([0]*len(df))).tolist()

        # Find first non-zero total value index
        first_nonzero_idx = None
        for i, total in enumerate(total_data):
            if total > 0:
                first_nonzero_idx = i
                break

        # Replace leading zeros with None
        if first_nonzero_idx is not None:
            for i in range(first_nonzero_idx):
                total_data[i] = None
                merged_data[i] = None
                percentage_data[i] = None

        # Total PRs
        chart_data["datasets"].append(
            {
                "label": f"{agent.title()} Total",
                "type": "bar",
                "data": total_data,
                "backgroundColor": colors[agent]["total"],
                "borderColor": colors[agent]["total"],
                "borderWidth": 1,
                "yAxisID": "y",
                "order": 2,
            }
        )

        # Merged PRs
        chart_data["datasets"].append(
            {
                "label": f"{agent.title()} Merged",
                "type": "bar",
                "data": merged_data,
                "backgroundColor": colors[agent]["merged"],
                "borderColor": colors[agent]["merged"],
                "borderWidth": 1,
                "yAxisID": "y",
                "order": 2,
            }
        )

        # Success rate line
        chart_data["datasets"].append(
            {
                "label": f"{agent.title()} Success %",
                "type": "line",
                "data": percentage_data,
                "borderColor": colors[agent]["line"],
                "backgroundColor": "rgba(255, 255, 255, 0.8)",
                "borderWidth": 3,
                "pointRadius": 3,
                "pointHoverRadius": 5,
                "fill": False,
                "yAxisID": "y1",
                "order": 1,
            }
        )

    # Write JSON file
    json_file = docs_dir / "chart-data.json"
    with open(json_file, "w") as f:
        json.dump(chart_data, f, indent=2)

    print(f"Chart data exported: {json_file}")
    return True


def update_readme(df):
    """Render README.md from template with latest statistics"""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print(f"Warning: {readme_path} not found, skipping README update.")
        return False

    latest = df.iloc[-1]
    stats = build_stats(latest)

    context = {"agents": AGENTS, "stats": stats}
    content = env.get_template("readme_template.md").render(context)
    readme_path.write_text(content)
    print("README.md updated with latest statistics.")
    return True


def update_github_pages(df):
    """Render the GitHub Pages site from template with latest statistics"""
    index_path = Path("docs/index.html")
    if not index_path.exists():
        print(f"Warning: {index_path} not found, skipping GitHub Pages update.")
        return False

    latest = df.iloc[-1]
    stats = build_stats(latest)
    timestamp = dt.datetime.now().strftime("%B %d, %Y %H:%M UTC")

    # Simple context - just the essentials
    context = {"agents": AGENTS, "stats": stats, "timestamp": timestamp}

    content = env.get_template("index_template.html").render(context)
    index_path.write_text(content)
    print("GitHub Pages updated with latest statistics and enhanced analytics.")
    return True


if __name__ == "__main__":
    generate_chart()
