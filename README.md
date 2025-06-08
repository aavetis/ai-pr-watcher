### PR Analytics: Volume vs Success Rate (auto‑updated)

View the [interactive dashboard](https://aavetis.github.io/ai-pr-watcher/) for these statistics.

## Data sources

Explore the GitHub search queries used:

- **All Copilot PRs**: [is:pr head:copilot/](https://github.com/search?q=is:pr+head:copilot/&type=pullrequests)
- **Merged Copilot PRs**: [is:pr head:copilot/ is:merged](https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests)
- **All Codex PRs**: [is:pr head:codex/](https://github.com/search?q=is:pr+head:codex/&type=pullrequests)
- **Merged Codex PRs**: [is:pr head:codex/ is:merged](https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests)
- **All Cursor PRs**: [is:pr head:cursor/](https://github.com/search?q=is:pr+head:cursor/&type=pullrequests)
- **Merged Cursor PRs**: [is:pr head:cursor/ is:merged](https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests)
- **All Devin PRs**: [author:devin-ai-integration[bot]](https://github.com/search?q=author:devin-ai-integration[bot]&type=pullrequests)
- **Merged Devin PRs**: [author:devin-ai-integration[bot] is:merged](https://github.com/search?q=author:devin-ai-integration[bot]+is:merged&type=pullrequests)

## Testing

Run simple tests to verify core functionality:

```bash
python test_pr_tracker.py
```

The test verifies:
- Required files exist (collect_data.py, generate_chart.py, README.md)
- CSV operations work correctly
- Data collection module imports and has required functions
- Chart generation module is available (when dependencies installed)
- Basic data processing works with existing data

This simple test helps ensure that core functionality works after any code changes.

---

![chart](docs/chart.png)

## Current Statistics

| Project | Total PRs | Merged PRs | Merge Rate |
| ------- | --------- | ---------- | ---------- |
| Copilot | 13,960 | 5,330 | 38.18% |
| Codex   | 199,786 | 165,861 | 83.02% |
| Cursor  | 668 | 508 | 76.05% |
| Devin   | 27,857 | 16,946 | 60.83% |