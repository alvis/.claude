# GIT-PR-STACK-04: Behaviour Changes Behind Feature Flags

## Severity

error

## Intent

Behaviour changes ship behind a feature flag unless the change is **all three** of: tiny, isolated, and reversible by simple revert. The flag PR (`GIT-PR-TYPE-01` category `feature-flag`) names the flag and states its default state; the implementation PR consumes the flag; a later `cleanup` PR retires the flag once the rollout is complete.

This rule is the safety net that makes stacked merges practical: each PR can land independently because behaviour stays gated until the whole stack is in.

## Fix

Three-PR pattern:

```text
order-archive/01-flag    feat(orders): [feature-flag] add orders.archive (default off)
order-archive/02-impl    feat(orders): [implementation] archiveOrder gated on orders.archive
order-archive/03-cleanup chore(orders): [cleanup] remove orders.archive flag (default on, week 4)
```

Flag PR body MUST state name and default:

```markdown
## Category
feature-flag

## Flag
- Name: `orders.archive`
- Default: off
- Owner: payments-platform team
- Removal target: 2026-05-20 (4 weeks)
- Rollout plan: 1 % -> 10 % -> 50 % -> 100 % over 2 weeks
```

Implementation PR consumes the flag:

```typescript
async function archiveOrder(input: ArchiveOrderInput): Promise<void> {
  if (!flags.isEnabled("orders.archive", input.merchantId)) {
    throw new FeatureDisabledError("orders.archive");
  }
  // ...
}
```

### When the "tiny / isolated / reversible" exemption applies

All three must hold:

- **Tiny**: green-zone PR, single function or a handful of lines.
- **Isolated**: no cross-module ripple; no migration; no consumer change.
- **Reversible**: `git revert` cleanly restores prior behaviour with no data implications.

A typo fix in user-facing copy qualifies. A pricing-engine swap does not.

## Edge Cases

- Migrations always pair with a flag (`GIT-PR-TYPE-03`); the migration is shape-only, the flag governs whether code uses the new shape.
- Flag retirement is a real PR (`cleanup`), not a passive timeout. The retirement PR also deletes the flag's config, telemetry, and tests for both branches.
- Internal-only experiments behind a kill switch satisfy this rule even when the "flag" is a config toggle rather than a typed flag system.

## Related

GIT-PR-TYPE-01, GIT-PR-TYPE-03, GIT-PR-SIZE-02, GIT-PR-STACK-02, GIT-PR-STACK-05
