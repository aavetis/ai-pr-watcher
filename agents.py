AGENTS = [
    {
        "slug": "copilot",
        "name": "Copilot",
        "display": "GitHub Copilot",
        "link": "https://docs.github.com/en/copilot/using-github-copilot/coding-agent/using-copilot-to-work-on-an-issue",
        "queries": {
            "total": "is:pr+head:copilot/",
            "merged": "is:pr+head:copilot/+is:merged"
        },
        "colors": {"total": "#87CEEB", "merged": "#4682B4", "line": "#000080", "icon": "#87ceeb"}
    },
    {
        "slug": "codex",
        "name": "Codex",
        "display": "OpenAI Codex",
        "link": "https://openai.com/index/introducing-codex/",
        "queries": {
            "total": "is:pr+head:codex/",
            "merged": "is:pr+head:codex/+is:merged"
        },
        "colors": {"total": "#FFA07A", "merged": "#CD5C5C", "line": "#8B0000", "icon": "#ff6b6b"}
    },
    {
        "slug": "cursor",
        "name": "Cursor",
        "display": "Cursor Agents",
        "link": "https://docs.cursor.com/background-agent",
        "queries": {
            "total": "is:pr+head:cursor/",
            "merged": "is:pr+head:cursor/+is:merged"
        },
        "colors": {"total": "#DDA0DD", "merged": "#9370DB", "line": "#800080", "icon": "#9b59b6"}
    },
    {
        "slug": "devin",
        "name": "Devin",
        "display": "Devin",
        "link": "https://devin.ai/pricing",
        "queries": {
            "total": "author:devin-ai-integration[bot]",
            "merged": "author:devin-ai-integration[bot]+is:merged"
        },
        "colors": {"total": "#98FB98", "merged": "#228B22", "line": "#006400", "icon": "#52c41a"}
    },
    {
        "slug": "codegen",
        "name": "Codegen",
        "display": "Codegen",
        "link": "https://codegen.com/",
        "queries": {
            "total": "author:codegen-sh[bot]",
            "merged": "author:codegen-sh[bot]+is:merged"
        },
        "colors": {"total": "#FFE4B5", "merged": "#DAA520", "line": "#B8860B", "icon": "#daa520"}
    }
]
