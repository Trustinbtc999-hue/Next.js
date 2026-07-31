# GitHub MCP Server v1.6.0 Release Notes

Released: 2026-07-15

## Highlights ⭐️

### Tool Response Filtering (Insiders)

A new `fields` parameter has been added to selected tools when running in **Insiders mode**. This allows models to specify exactly which fields they need when calling a tool, reducing the size of tool responses and optimizing context window usage.

Tools with the new `fields` parameter include:
- `search_code`
- `get_file_contents`
- Six additional list/search tools

## What's Changed

### New Features

- **`update_issue_assignees`**: Added `is_suggestion` and `rationale` parameters to provide models with a way to explain why assignees are being suggested.
- **`close_issue`**: Added `rationale` and `confidence` parameters when closing an issue.
- **`issue_read` (get)**: Enriched with hierarchy relationship signals — responses now include best-effort `has_parent` and `has_children` flags, along with optional `parent` and `sub_issues_summary` relationship summaries.
- **Projects fields**: Added name-based resolution for Projects fields, making it easier to filter issues by custom field values without needing to look up field IDs first.
- **Issue dependencies**: Reimplemented on the go-github v89 REST API.

### Dependency Updates

- Upgraded `go-sdk` to v1.7.0-pre.1 (new MCP spec)
- Bumped `go-github` from v87 to v89 with breaking-change resolution
- Updated `golang.org/x/net` from 0.38.0 to 0.55.0
- Updated `goreleaser/goreleaser-action` from 7.2.2 to 7.2.3
- Updated `docker/build-push-action` from 7.2.0 to 7.3.0

## New Contributors

- @insonmia0126-lovable — first contribution (added README community resource links)
- @veralizeth — first contribution (name-based resolution for Projects fields)

## Full Changelog

https://github.com/github/github-mcp-server/compare/v1.5.0...v1.6.0
