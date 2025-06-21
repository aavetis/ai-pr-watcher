#!/usr/bin/env python3
# PR‑tracker: generates a combo chart from the collected PR data.
# deps: pandas, matplotlib, numpy

from pathlib import Path
from string import Template
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import re
import json
from agents import AGENTS


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
        print(f"Limited chart to 8 data points evenly distributed across {total_points} total points.")

    # Calculate success percentages for each agent
    for agent in AGENTS:
        slug = agent["slug"]
        perc_col = f"{slug}_percentage"
        total_col = f"{slug}_total"
        merged_col = f"{slug}_merged"
        df[perc_col] = df.apply(
            lambda row: (row[merged_col] / row[total_col] * 100)
            if row[total_col] > 0
            else 0,
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

    # Bar and line charts for each agent
    marker_styles = ["o", "s", "d", "^", "v", "x", "*", "P", "X", "+"]
    bar_handles_total = []
    bar_handles_merged = []
    line_handles = []

    offsets = (np.arange(len(AGENTS)) - len(AGENTS) // 2) * width

    for idx, (agent, offset) in enumerate(zip(AGENTS, offsets)):
        slug = agent["slug"]
        name = agent["name"]
        colors = agent["colors"]

        bars_total = ax1.bar(
            x + offset,
            df[f"{slug}_total"],
            width,
            label=f"{name} Total",
            alpha=0.7,
            color=colors["total"],
        )
        bars_merged = ax1.bar(
            x + offset,
            df[f"{slug}_merged"],
            width,
            label=f"{name} Merged",
            alpha=1.0,
            color=colors["merged"],
        )

        line = ax2.plot(
            x,
            df[f"{slug}_percentage"],
            marker_styles[idx % len(marker_styles)] + "-",
            color=colors["line"],
            linewidth=3,
            markersize=10,
            label=f"{name} Success %",
            markerfacecolor="white",
            markeredgewidth=2,
            markeredgecolor=colors["line"],
        )

        bar_handles_total.append(bars_total)
        bar_handles_merged.append(bars_merged)
        line_handles.append(line)

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

    for bars in bar_handles_total + bar_handles_merged:
        add_value_labels(ax1, bars)

    # Add percentage labels on line points (with validation and skip 0.0%)
    for i in range(len(df)):
        for idx, agent in enumerate(AGENTS):
            perc = df.iloc[i][f"{agent['slug']}_percentage"]
            if pd.notna(perc) and perc > 0:
                if idx == 0:
                    y_off = 15
                else:
                    y_off = -20 - (idx - 1) * 15
                ax2.annotate(
                    f"{perc:.1f}%",
                    (i, perc),
                    textcoords="offset points",
                    xytext=(0, y_off),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color=agent['colors']['line'],
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
    chart_data = {
        "labels": [],
        "datasets": []
    }
    
    # Format timestamps for labels
    for _, row in df.iterrows():
        timestamp = row["timestamp"]
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        chart_data["labels"].append(timestamp.strftime("%m/%d %H:%M"))
    
    # Color scheme matching the Python chart
    colors = {a["slug"]: a["colors"] for a in AGENTS}
    
    # Add bar datasets for totals and merged PRs
    for agent in [a["slug"] for a in AGENTS]:
        # Process data to replace leading zeros with None (null in JSON)
        total_data = df[f"{agent}_total"].tolist()
        merged_data = df[f"{agent}_merged"].tolist()
        percentage_data = df[f"{agent}_percentage"].tolist()
        
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
        chart_data["datasets"].append({
            "label": f"{agent.title()} Total",
            "type": "bar",
            "data": total_data,
            "backgroundColor": colors[agent]["total"],
            "borderColor": colors[agent]["total"],
            "borderWidth": 1,
            "yAxisID": "y",
            "order": 2
        })
        
        # Merged PRs
        chart_data["datasets"].append({
            "label": f"{agent.title()} Merged",
            "type": "bar",
            "data": merged_data,
            "backgroundColor": colors[agent]["merged"],
            "borderColor": colors[agent]["merged"],
            "borderWidth": 1,
            "yAxisID": "y",
            "order": 2
        })
        
        # Success rate line
        chart_data["datasets"].append({
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
            "order": 1
        })
    
    # Write JSON file
    json_file = docs_dir / "chart-data.json"
    with open(json_file, "w") as f:
        json.dump(chart_data, f, indent=2)
    
    print(f"Chart data exported: {json_file}")
    return True


def build_readme_sources():
    lines = []
    for a in AGENTS:
        lines.append(
            f"- **All {a['name']} PRs**: [is:pr head:{a['slug']}/](https://github.com/search?q={a['queries']['total']}&type=pullrequests)"
        )
        lines.append(
            f"- **Merged {a['name']} PRs**: [is:pr head:{a['slug']}/ is:merged](https://github.com/search?q={a['queries']['merged']}&type=pullrequests)"
        )
    return "\n".join(lines)


def build_readme_table(latest):
    rows = []
    for a in AGENTS:
        slug = a["slug"]
        total = latest[f"{slug}_total"]
        merged = latest[f"{slug}_merged"]
        rate = merged / total * 100 if total > 0 else 0
        rows.append(
            f"| {a['name']} | {total:,} | {merged:,} | {rate:.2f}% |"
        )
    return "\n".join(rows)


def build_html_rows(latest):
    rows = []
    for a in AGENTS:
        slug = a["slug"]
        total = latest[f"{slug}_total"]
        merged = latest[f"{slug}_merged"]
        rate = merged / total * 100 if total > 0 else 0
        rows.append(
            f"<tr data-agent=\"{slug}\">"
            f"<td class=\"agent-cell\"><div class=\"agent-info\">"
            f"<span class=\"agent-icon\" style=\"background-color: {a['colors']['icon']}\"></span>"
            f"<a href=\"{a['link']}\" target=\"_blank\" class=\"agent-link\">{a['display']}</a>"
            f"</div></td>"
            f"<td class=\"metric-cell\"><a href=\"https://github.com/search?q={a['queries']['total']}&type=pullrequests\" target=\"_blank\" class=\"metric-link\"><span id=\"{slug}-total\">{total:,}</span></a></td>"
            f"<td class=\"metric-cell\"><a href=\"https://github.com/search?q={a['queries']['merged']}&type=pullrequests\" target=\"_blank\" class=\"metric-link\"><span id=\"{slug}-merged\">{merged:,}</span></a></td>"
            f"<td class=\"rate-cell\"><span id=\"{slug}-rate\">{rate:.2f}%</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def build_toggle_buttons():
    buttons = []
    for a in AGENTS:
        btn_id = f"toggle{a['name'].replace(' ', '')}"
        buttons.append(
            f"<button id=\"{btn_id}\" class=\"toggle-btn active\" data-agent=\"{a['slug']}\">"
            f"<span class=\"toggle-icon\" style=\"background-color: {a['colors']['icon']}\"></span>{a['display']}</button>"
        )
    return "\n".join(buttons)


def build_substitutions(df):
    """Prepare placeholder values for README and HTML templates."""
    latest = df.iloc[-1]
    return {
        "DATA_SOURCES": build_readme_sources(),
        "STATS_ROWS": build_readme_table(latest),
        "AGENT_TABLE_ROWS": build_html_rows(latest),
        "AGENT_TOGGLES": build_toggle_buttons(),
        "AGENT_LIST_JS": json.dumps([a["slug"] for a in AGENTS]),
        "AGENT_REGEX": "|".join(a["slug"] for a in AGENTS),
        "LAST_UPDATED": dt.datetime.now().strftime("%B %d, %Y %H:%M UTC"),
    }


def update_readme(df):
    """Render README.md from template with the latest statistics."""
    template_path = Path("templates/readme_template.md")
    output_path = Path("README.md")

    if not template_path.exists():
        print(f"Warning: {template_path} missing, skipping README update.")
        return False

    subs = build_substitutions(df)

    template_text = template_path.read_text()
    rendered = Template(template_text).substitute(subs)
    output_path.write_text(rendered)
    print("README.md updated with latest statistics.")
    return True


def update_github_pages(df):
    """Render the GitHub Pages HTML from a template."""
    template_path = Path("templates/index_template.html")
    output_path = Path("docs/index.html")

    if not template_path.exists():
        print(f"Warning: {template_path} missing, skipping GitHub Pages update.")
        return False

    subs = build_substitutions(df)

    template_text = template_path.read_text()
    rendered = Template(template_text).substitute(subs)
    output_path.write_text(rendered)
    print("GitHub Pages updated with latest statistics.")
    return True


if __name__ == "__main__":
    generate_chart()
