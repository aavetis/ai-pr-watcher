### PR Analytics: Volume vs Success Rate (auto-updated)

View the [interactive dashboard](https://aavetis.github.io/ai-pr-watcher/) for these statistics.

## Data sources

Explore the GitHub search queries used:



- **All Copilot PRs**: [https://github.com/search?q=is:pr+head:copilot/&type=pullrequests](https://github.com/search?q=is:pr+head:copilot/&type=pullrequests)
- **Merged Copilot PRs**: [https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests)
  

- **All Codex PRs**: [https://github.com/search?q=is:pr+head:codex/&type=pullrequests](https://github.com/search?q=is:pr+head:codex/&type=pullrequests)
- **Merged Codex PRs**: [https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests)
  

- **All Cursor PRs**: [https://github.com/search?q=is:pr+head:cursor/&type=pullrequests](https://github.com/search?q=is:pr+head:cursor/&type=pullrequests)
- **Merged Cursor PRs**: [https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests)
  

- **All Devin PRs**: [https://github.com/search?q=is:pr+author:devin-ai-integration[bot]&type=pullrequests](https://github.com/search?q=is:pr+author:devin-ai-integration[bot]&type=pullrequests)
- **Merged Devin PRs**: [https://github.com/search?q=is:pr+author:devin-ai-integration[bot]+is:merged&type=pullrequests](https://github.com/search?q=is:pr+author:devin-ai-integration[bot]+is:merged&type=pullrequests)
  

- **All Codegen PRs**: [https://github.com/search?q=is:pr+author:codegen-sh[bot]&type=pullrequests](https://github.com/search?q=is:pr+author:codegen-sh[bot]&type=pullrequests)
- **Merged Codegen PRs**: [https://github.com/search?q=is:pr+author:codegen-sh[bot]+is:merged&type=pullrequests](https://github.com/search?q=is:pr+author:codegen-sh[bot]+is:merged&type=pullrequests)
  

---

![chart](docs/chart.png)

---

## About the Cosine Agent

**Cosine** is an advanced coding agent for developers, now tracked alongside Copilot, Codex, Cursor, Devin, and Codegen.  
- **Color in charts:** ![#FF00FF](https://placehold.co/15x15/FF00FF/FF00FF.png) `#FF00FF` (magenta family, used for totals/merged/lines)
- **Learn more:** [https://cosine.dev/](https://cosine.dev/)

## Current Statistics

| Project | Total PRs | Merged PRs | Merge Rate |
| ------- | --------- | ---------- | ---------- |{%- for agent in agents %}
| {{ agent.display }} | {{ stats[agent.key].total | comma }} | {{ stats[agent.key].merged | comma }} | {{ stats[agent.key].rate | round(2) }}% |{%- endfor %}

## Current Statistics

| Project | Total PRs | Merged PRs | Merge Rate |
| ------- | --------- | ---------- | ---------- |
| Copilot | 18,737 | 11,333 | 60.48% |
| Codex | 502,277 | 432,462 | 86.1% |
| Cursor | 2,657 | 1,949 | 73.35% |
| Devin | 29,120 | 18,578 | 63.8% |
| Codegen | 4,163 | 1,695 | 40.72% |