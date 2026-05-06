# Phase 1 -- Plan (Detail)

Loaded by `SKILL.md` Step 1. Resolves the target URL (and optional source path), viewports, and scope into a single plan object that feeds the CLI.

**Step Configuration**:
- **Purpose**: Resolve the target URL (and optional source path), viewports, and scope into a single plan object that feeds the CLI
- **Input**: User-provided URL or project path, optional scope, optional `--all-pages`
- **Output**: `{ target_url, source_path?, scope, viewports[], all_pages }` ready for Phase 2
- **Parallel Execution**: No

## 1.1 Parse Input Mode

**URL mode** (URL provided directly):
- `target_url` = the provided URL
- `source_path` = omitted

**Source code mode** (project path provided):
1. Detect project type by checking for marker files:
   - `next.config.*` or `next.config.ts` --> Next.js (`npm run dev` or `npx next dev`)
   - `vite.config.*` --> Vite (`npm run dev` or `npx vite`)
   - `react-scripts` in package.json --> CRA (`npm start`)
   - `index.html` at root --> static (`npx serve .`)
2. Install dependencies if needed (`npm install`)
3. Start the dev server in background
4. Wait for the server to be ready (check stdout for "ready" / "listening" / URL output)
5. `target_url` = the dev server URL
6. `source_path` = the project path (passed to the CLI as `--source` so it can discover orphan/uncrawled routes from source code)

**Error handling**:
- If dev server fails to start: check `package.json` scripts, try alternative commands, report to user if all fail
- If port is already in use: try the dev server's default port, or detect the running server URL

## 1.2 Resolve Viewports

Default viewports (always emitted to the CLI):

| Viewport | Dimensions |
|----------|-----------|
| Desktop  | 1440x900 |
| Tablet   | 768x1024 |
| Mobile   | 390x844 (mobile=true, touch=true) |

## 1.3 Determine Scope

| Scope | Rules | When |
|-------|-------|------|
| `full` (default) | All 60 rules, all categories | No scope specified |
| `quick` | Text + structure only (17 rules) | User says "quick audit" |
| Category-specific | Rules in requested category only | User specifies category |

## 1.4 Emit Plan

Output of Phase 1:

```json
{
  "target_url": "https://example.com",
  "source_path": "/abs/path/to/project",
  "scope": "full",
  "viewports": ["desktop", "tablet", "mobile"],
  "all_pages": false
}
```

`source_path` is omitted in URL mode. This object feeds directly into the Phase 2 CLI invocation.
