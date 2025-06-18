#!/usr/bin/env python3
# PR‑tracker: counts Copilot / Codex PRs and saves data to CSV.
# Tracks merged PRs (not just approved ones)
# deps: requests

import csv
import datetime as dt
import re
from pathlib import Path
import requests

# Basic headers for GitHub public API
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "PR-Watcher"}

# Search queries - tracking merged PRs
Q = {
    "language:cpp+is:pr+head:copilot/": "copilot_total",
    "language:cpp+is:pr+head:copilot/+is:merged": "copilot_merged",
    "language:cpp+is:pr+head:codex/": "codex_total",
    "language:cpp+is:pr+head:codex/+is:merged": "codex_merged",
    "language:cpp+is:pr+head:cursor/": "cursor_total",
    "language:cpp+is:pr+head:cursor/+is:merged": "cursor_merged",
    "language:cpp+author:devin-ai-integration[bot]": "devin_total",
    "language:cpp+author:devin-ai-integration[bot]+is:merged": "devin_merged",
    "language:cpp+author:codegen-sh[bot]": "codegen_total",
    "language:cpp+author:codegen-sh[bot]+is:merged": "codegen_merged",
}


def collect_data():
    # Get data from GitHub API
    cnt = {}
    for query, key in Q.items():
        r = requests.get(
            f"https://api.github.com/search/issues?q={query}",
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        cnt[key] = r.json()["total_count"]

    # Save data to CSV
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y‑%m‑%d %H:%M:%S")
    row = [
        timestamp,
        cnt["copilot_total"],
        cnt["copilot_merged"],
        cnt["codex_total"],
        cnt["codex_merged"],
        cnt["cursor_total"],
        cnt["cursor_merged"],
        cnt["devin_total"],
        cnt["devin_merged"],
        cnt["codegen_total"],
        cnt["codegen_merged"],
    ]

    csv_file = Path("data.csv")
    is_new_file = not csv_file.exists()
    with csv_file.open("a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(
                [
                    "timestamp",
                    "copilot_total",
                    "copilot_merged",
                    "codex_total",
                    "codex_merged",
                    "cursor_total",
                    "cursor_merged",
                    "devin_total",
                    "devin_merged",
                    "codegen_total",
                    "codegen_merged",
                ]
            )
        writer.writerow(row)

    return csv_file


def update_html_with_latest_data():
    """Update the HTML file with the latest statistics from the chart data."""
    # The HTML will be updated by JavaScript automatically when chart-data.json loads
    # This is a placeholder for any additional HTML updates needed
    html_file = Path("docs/index.html")
    if not html_file.exists():
        print("HTML file not found, skipping HTML update")
        return

    # Update the last updated timestamp in the HTML
    html_content = html_file.read_text(encoding='utf-8')

    # Get current timestamp in the format used in the HTML
    now = dt.datetime.now(dt.UTC)
    timestamp_str = now.strftime("%B %d, %Y %H:%M UTC")

    # Update the timestamp in the HTML
    updated_html = re.sub(
        r'<span id="last-updated">[^<]*</span>',
        f'<span id="last-updated">{timestamp_str}</span>',
        html_content,
    )

    html_file.write_text(updated_html, encoding='utf-8')
    print(f"Updated HTML timestamp to: {timestamp_str}")


if __name__ == "__main__":
    collect_data()
    update_html_with_latest_data()
    print("Data collection complete. To generate chart, run generate_chart.py")
