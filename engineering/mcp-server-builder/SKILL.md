---
name: "mcp-server-builder"
description: "Generate a production-ready MCP server scaffold (Python or TypeScript) from an OpenAPI spec with openapi_to_mcp.py — converts paths/operations into an MCP tool manifest + starter server, deriving tool names from operationId. Validate the manifest with mcp_validator.py (duplicate names, missing descriptions, invalid schema shape, empty required fields, naming hygiene; non-zero exit in --strict). Use when exposing a REST API to an LLM agent, replacing brittle browser automation with typed tools, bootstrapping an MCP server from an OpenAPI/Swagger spec, or gating MCP tool quality in CI — e.g. 'build an MCP server from this openapi.json', 'turn our API into MCP tools', 'validate my MCP tool manifest'."
---

# MCP Server Builder

Ship MCP servers from API contracts instead of hand-written tool wrappers.
OpenAPI is the source of truth: two stdlib-only tools turn a spec into a tool
manifest + starter server, then validate the manifest before integration.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/openapi_to_mcp.py` | OpenAPI spec → MCP tool manifest + Python/TypeScript server scaffold |
| `scripts/mcp_validator.py` | Validate a tool manifest for production failures (CI gate with `--strict`) |

## Workflow

Generate, then validate. If the validator reports errors, fix the spec (or the
generated manifest) and re-run until strict mode exits clean.

```bash
# 1. Scaffold from a spec (JSON or YAML). --input or stdin; --language python|typescript.
python3 scripts/openapi_to_mcp.py \
  --input openapi.json --server-name billing-mcp \
  --language python --output-dir ./out --format text
cat openapi.json | python3 scripts/openapi_to_mcp.py --server-name billing-mcp --language typescript

# 2. Validate the generated manifest. --strict exits non-zero on errors (CI gate).
python3 scripts/mcp_validator.py --input out/tool_manifest.json --strict --format text
```

`openapi_to_mcp.py` derives tool names from `operationId` when available,
producing `tool_manifest.json` plus a starter server in the chosen language.
`mcp_validator.py` checks for duplicate names, invalid schema shape, missing
descriptions, empty required fields, and naming hygiene. Both accept
`--format text|json`. Validation criteria:
[references/validation-checklist.md](references/validation-checklist.md).

## Contract design

- Use `operationId` as the canonical tool name; one task intent per tool, no mega-tools.
- Every tool needs a verb-first name and a concise description (agents pick tools by description).
- Type every required field explicitly; destructive actions take a confirmation parameter.
- Return structured errors (`code`, `message`, `details`) so agents can recover.
- Keep secrets in env, never in tool schemas; keep an explicit outbound-host allowlist.

## Versioning

Additive fields only for non-breaking updates. Never rename a tool in place —
introduce a new tool ID for breaking behavior changes, and pair every contract
change with a changelog entry. Keep backward compatibility for at least one
release window.

## Testing

- Unit: OpenAPI operation → MCP tool schema transformation.
- Contract: snapshot `tool_manifest.json` and review the diff in PR.
- Integration: call generated handlers against a staging API.
- Resilience: simulate 4xx/5xx upstream errors, verify structured responses.

## References

- [references/openapi-extraction-guide.md](references/openapi-extraction-guide.md) — extracting tools from paths/operations
- [references/python-server-template.md](references/python-server-template.md) — Python runtime scaffold
- [references/typescript-server-template.md](references/typescript-server-template.md) — TypeScript runtime scaffold
- [references/validation-checklist.md](references/validation-checklist.md) — manifest quality gates
- [README.md](README.md)
