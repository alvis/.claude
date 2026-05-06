# Reporting Output Formats

Use this reference during Step 2 (Reporting) to render the final console/markdown summary. The active format is gated on the runtime environment detected in Phase 1: **CI/Non-Interactive** vs **Interactive**.

## Common fields (both formats)

- Review scopes: `[list of scopes reviewed]`
- Overall status: `[PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]`
- Per-area file listing with each file's verdict
- Aggregate open-issue counts: P0, P1, P2, P3
- Path to `<out>/README.md` index

## CI / Non-Interactive Format

```markdown
# Code Review Summary

**Generated**: [timestamp]
**Review Scopes**: [scopes reviewed]
**Overall Status**: [PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]

## Area Files

- [Security](./reviews/SECURITY.md) — ❌ FAIL — 3 issues (P0:1, P1:2, P2:0, P3:0)
- [Quality](./reviews/QUALITY.md) — ✅ PASS
- [Testing](./reviews/TESTING.md) — ❌ FAIL — 2 issues (P0:0, P1:0, P2:1, P3:1)
- [Docs](./reviews/DOCS.md) — ✅ PASS
- [Style](./reviews/STYLE.md) — ✅ PASS
- [Correctness](./reviews/CORRECTNESS.md) — ❌ FAIL — 1 issue (P0:0, P1:1, P2:0, P3:0)

## Aggregate

- P0: [N], P1: [N], P2: [N], P3: [N]

Index: `./reviews/README.md`
```

## Interactive Format

```
Code Review Complete

Area files written under reviews/:
  SECURITY.md    ❌ FAIL — 3 issues (P0:1, P1:2, P2:0, P3:0)
  QUALITY.md     ✅ PASS
  TESTING.md     ❌ FAIL — 2 issues (P0:0, P1:0, P2:1, P3:1)
  DOCS.md        ✅ PASS
  STYLE.md       ✅ PASS
  CORRECTNESS.md ❌ FAIL — 1 issue (P0:0, P1:1, P2:0, P3:0)

Aggregate open issues: P0:1, P1:3, P2:1, P3:1

FAIL areas: SECURITY, TESTING, CORRECTNESS

Index: reviews/README.md
```
