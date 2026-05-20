---
paths: "**/*.{yaml,yml}"
---

# YAML Guidelines

- Use 2 spaces for indentation
- **IMPORTANT**: Use only `true`/`false`, never `yes`/`no`/`on`/`off` (YAML 1.2 compatibility)
- Use `|` (literal) or `>` (folded) for multi-line strings, not `\n` escapes
- Use `yq` for querying and transforming YAML
