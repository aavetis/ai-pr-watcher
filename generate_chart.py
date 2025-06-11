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

    # Calculate percentages with safety checks
    df["claude_percentage"] = df.apply(
        lambda row: (
            (row["claude_merged"] / row["claude_total"] * 100)
            if row["claude_total"] > 0
            else 0
        ),
        axis=1,
    )
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
    # Adjust bar width based on number of data points (6 groups now)
    width = min(0.13, 0.8 / max(1, num_points * 0.6))

    # Bar charts for totals and merged
    bars_claude_total = ax1.bar(
        x - 2.5*width,
        df["claude_total"],
        width,
        label="Claude Total",
        alpha=0.7,
        color="#FFB6C1",
    )
    bars_claude_merged = ax1.bar(
        x - 2.5*width,
        df["claude_merged"],
        width,
        label="Claude Merged",
        alpha=1.0,
        color="#FF69B4",
    )

    bars_copilot_total = ax1.bar(
        x - 1.5*width,
        df["copilot_total"],
        width,
        label="Copilot Total",
        alpha=0.7,
        color="#87CEEB",
    )
    bars_copilot_merged = ax1.bar(
        x - 1.5*width,
        df["copilot_merged"],
        width,
        label="Copilot Merged",
        alpha=1.0,
        color="#4682B4",
    )

    bars_codex_total = ax1.bar(
        x - 0.5*width,
        df["codex_total"],
        width,
        label="Codex Total",
        alpha=0.7,
        color="#FFA07A",
    )
    bars_codex_merged = ax1.bar(
        x - 0.5*width,
        df["codex_merged"],
        width,
        label="Codex Merged",
        alpha=1.0,
        color="#CD5C5C",
    )

    bars_cursor_total = ax1.bar(
        x + 0.5*width,
        df["cursor_total"],
        width,
        label="Cursor Total",
        alpha=0.7,
        color="#DDA0DD",
    )
    bars_cursor_merged = ax1.bar(
        x + 0.5*width,
        df["cursor_merged"],
        width,
        label="Cursor Merged",
        alpha=1.0,
        color="#9370DB",
    )

    bars_devin_total = ax1.bar(
        x + 1.5*width,
        df["devin_total"],
        width,
        label="Devin Total",
        alpha=0.7,
        color="#98FB98",
    )
    bars_devin_merged = ax1.bar(
        x + 1.5*width,
        df["devin_merged"],
        width,
        label="Devin Merged",
        alpha=1.0,
        color="#228B22",
    )

    bars_codegen_total = ax1.bar(
        x + 2.5*width,
        df["codegen_total"],
        width,
        label="Codegen Total",
        alpha=0.7,
        color="#FFE4B5",
    )
    bars_codegen_merged = ax1.bar(
        x + 2.5*width,
        df["codegen_merged"],
        width,
        label="Codegen Merged",
        alpha=1.0,
        color="#DAA520",
    )

    # Line charts for percentages (on secondary y-axis)
    line_claude = ax2.plot(
        x,
        df["claude_percentage"],
        "*-",
        color="#C71585",
        linewidth=3,
        markersize=10,
        label="Claude Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#C71585",
    )

    line_copilot = ax2.plot(
        x,
        df["copilot_percentage"],
        "o-",
        color="#000080",
        linewidth=3,
        markersize=10,
        label="Copilot Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#000080",
    )

    line_codex = ax2.plot(
        x,
        df["codex_percentage"],
        "s-",
        color="#8B0000",
        linewidth=3,
        markersize=10,
        label="Codex Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#8B0000",
    )

    line_cursor = ax2.plot(
        x,
        df["cursor_percentage"],
        "d-",
        color="#800080",
        linewidth=3,
        markersize=10,
        label="Cursor Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#800080",
    )

    line_devin = ax2.plot(
        x,
        df["devin_percentage"],
        "^-",
        color="#006400",
        linewidth=3,
        markersize=10,
        label="Devin Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#006400",
    )

    line_codegen = ax2.plot(
        x,
        df["codegen_percentage"],
        "v-",
        color="#B8860B",
        linewidth=3,
        markersize=10,
        label="Codegen Success %",
        markerfacecolor="white",
        markeredgewidth=2,
        markeredgecolor="#B8860B",
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

    add_value_labels(ax1, bars_claude_total)
    add_value_labels(ax1, bars_claude_merged)
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
    for i, (cl_pct, cop_pct, cod_pct, cur_pct, dev_pct, cg_pct) in enumerate(
        zip(df["claude_percentage"], df["copilot_percentage"], df["codex_percentage"], df["cursor_percentage"], df["devin_percentage"], df["codegen_percentage"])
    ):
        # Only add labels if percentages are valid numbers and not 0.0%
        if pd.notna(cl_pct) and pd.notna(cop_pct) and pd.notna(cod_pct) and pd.notna(cur_pct) and pd.notna(dev_pct) and pd.notna(cg_pct):
            if cl_pct > 0.0:
                ax2.annotate(
                    f"{cl_pct:.1f}%",
                    (i, cl_pct),
                    textcoords="offset points",
                    xytext=(0, 30),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#C71585",
                )
            if cop_pct > 0.0:
                ax2.annotate(
                    f"{cop_pct:.1f}%",
                    (i, cop_pct),
                    textcoords="offset points",
                    xytext=(0, 15),
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#000080",
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
                    color="#8B0000",
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
                    color="#800080",
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
                    color="#006400",
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
                    color="#B8860B",
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
    colors = {
        "claude": {"total": "#FFB6C1", "merged": "#FF69B4", "line": "#C71585"},
        "copilot": {"total": "#87CEEB", "merged": "#4682B4", "line": "#000080"},
        "codex": {"total": "#FFA07A", "merged": "#CD5C5C", "line": "#8B0000"},
        "cursor": {"total": "#DDA0DD", "merged": "#9370DB", "line": "#800080"},
        "devin": {"total": "#98FB98", "merged": "#228B22", "line": "#006400"},
        "codegen": {"total": "#FFE4B5", "merged": "#DAA520", "line": "#B8860B"}
    }
    
    # Add bar datasets for totals and merged PRs
    for agent in ["claude", "copilot", "codex", "cursor", "devin", "codegen"]:
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


def update_readme(df):
    """Update the README.md with the latest statistics"""
    readme_path = Path("README.md")

    # Skip if README doesn't exist
    if not readme_path.exists():
        print(f"Warning: {readme_path} not found, skipping README update.")
        return False

    # Get the latest data
    latest = df.iloc[-1]

    # Calculate merge rates
    claude_rate = latest.claude_merged / latest.claude_total * 100 if latest.claude_total > 0 else 0
    copilot_rate = latest.copilot_merged / latest.copilot_total * 100
    codex_rate = latest.codex_merged / latest.codex_total * 100
    cursor_rate = latest.cursor_merged / latest.cursor_total * 100 if latest.cursor_total > 0 else 0
    devin_rate = latest.devin_merged / latest.devin_total * 100 if latest.devin_total > 0 else 0
    codegen_rate = latest.codegen_merged / latest.codegen_total * 100 if latest.codegen_total > 0 else 0

    # Format numbers with commas
    claude_total = f"{latest.claude_total:,}"
    claude_merged = f"{latest.claude_merged:,}"
    copilot_total = f"{latest.copilot_total:,}"
    copilot_merged = f"{latest.copilot_merged:,}"
    codex_total = f"{latest.codex_total:,}"
    codex_merged = f"{latest.codex_merged:,}"
    cursor_total = f"{latest.cursor_total:,}"
    cursor_merged = f"{latest.cursor_merged:,}"
    devin_total = f"{latest.devin_total:,}"
    devin_merged = f"{latest.devin_merged:,}"
    codegen_total = f"{latest.codegen_total:,}"
    codegen_merged = f"{latest.codegen_merged:,}"

    # Create the new table content
    table_content = f"""## Current Statistics

| Project | Total PRs | Merged PRs | Merge Rate |
| ------- | --------- | ---------- | ---------- |
| Claude  | {claude_total} | {claude_merged} | {claude_rate:.2f}% |
| Copilot | {copilot_total} | {copilot_merged} | {copilot_rate:.2f}% |
| Codex   | {codex_total} | {codex_merged} | {codex_rate:.2f}% |
| Cursor  | {cursor_total} | {cursor_merged} | {cursor_rate:.2f}% |
| Devin   | {devin_total} | {devin_merged} | {devin_rate:.2f}% |
| Codegen | {codegen_total} | {codegen_merged} | {codegen_rate:.2f}% |"""

    # Read the current README content
    readme_content = readme_path.read_text()

    # Split content at the statistics header (if it exists)
    if "## Current Statistics" in readme_content:
        base_content = readme_content.split("## Current Statistics")[0].rstrip()
        new_content = f"{base_content}\n\n{table_content}"
    else:
        new_content = f"{readme_content}\n\n{table_content}"

    # Write the updated content back
    readme_path.write_text(new_content)
    print(f"README.md updated with latest statistics.")
    return True


def update_github_pages(df):
    """Update the GitHub Pages website with the latest statistics"""
    index_path = Path("docs/index.html")
    
    # Skip if index.html doesn't exist
    if not index_path.exists():
        print(f"Warning: {index_path} not found, skipping GitHub Pages update.")
        return False
    
    # Get the latest data
    latest = df.iloc[-1]
    
    # Calculate merge rates
    claude_rate = latest.claude_merged / latest.claude_total * 100 if latest.claude_total > 0 else 0
    copilot_rate = latest.copilot_merged / latest.copilot_total * 100
    codex_rate = latest.codex_merged / latest.codex_total * 100
    cursor_rate = latest.cursor_merged / latest.cursor_total * 100 if latest.cursor_total > 0 else 0
    devin_rate = latest.devin_merged / latest.devin_total * 100 if latest.devin_total > 0 else 0
    codegen_rate = latest.codegen_merged / latest.codegen_total * 100 if latest.codegen_total > 0 else 0

    # Format numbers with commas
    claude_total = f"{latest.claude_total:,}"
    claude_merged = f"{latest.claude_merged:,}"
    copilot_total = f"{latest.copilot_total:,}"
    copilot_merged = f"{latest.copilot_merged:,}"
    codex_total = f"{latest.codex_total:,}"
    codex_merged = f"{latest.codex_merged:,}"
    cursor_total = f"{latest.cursor_total:,}"
    cursor_merged = f"{latest.cursor_merged:,}"
    devin_total = f"{latest.devin_total:,}"
    devin_merged = f"{latest.devin_merged:,}"
    codegen_total = f"{latest.codegen_total:,}"
    codegen_merged = f"{latest.codegen_merged:,}"
    
    # Current timestamp for last updated
    timestamp = dt.datetime.now().strftime("%B %d, %Y %H:%M UTC")
    
    # Read the current index.html content
    index_content = index_path.read_text()
    
    # Update the table data
    index_content = re.sub(
        r'<td>Claude</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Claude</td>\n                        <td>{claude_total}</td>\n                        <td>{claude_merged}</td>\n                        <td>{claude_rate:.2f}%</td>',
        index_content
    )
    
    index_content = re.sub(
        r'<td>Copilot</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Copilot</td>\n                        <td>{copilot_total}</td>\n                        <td>{copilot_merged}</td>\n                        <td>{copilot_rate:.2f}%</td>',
        index_content
    )
    
    index_content = re.sub(
        r'<td>Codex</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Codex</td>\n                        <td>{codex_total}</td>\n                        <td>{codex_merged}</td>\n                        <td>{codex_rate:.2f}%</td>',
        index_content
    )
    
    index_content = re.sub(
        r'<td>Cursor</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Cursor</td>\n                        <td>{cursor_total}</td>\n                        <td>{cursor_merged}</td>\n                        <td>{cursor_rate:.2f}%</td>',
        index_content
    )
    
    index_content = re.sub(
        r'<td>Devin</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Devin</td>\n                        <td>{devin_total}</td>\n                        <td>{devin_merged}</td>\n                        <td>{devin_rate:.2f}%</td>',
        index_content
    )
    
    index_content = re.sub(
        r'<td>Codegen</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>',
        f'<td>Codegen</td>\n                        <td>{codegen_total}</td>\n                        <td>{codegen_merged}</td>\n                        <td>{codegen_rate:.2f}%</td>',
        index_content
    )
    
    # Update the last updated timestamp
    index_content = re.sub(
        r'<span id="last-updated">[^<]*</span>',
        f'<span id="last-updated">{timestamp}</span>',
        index_content
    )
    
    # Write the updated content back
    index_path.write_text(index_content)
    print(f"GitHub Pages updated with latest statistics.")
    return True


if __name__ == "__main__":
    generate_chart()
