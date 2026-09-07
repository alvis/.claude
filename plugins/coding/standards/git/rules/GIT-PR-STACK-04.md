# GIT-PR-STACK-04: Use Existing Feature-Flag Support

## Severity

error

## Intent

Apply this rule only when the target project supports feature flags and has an implemented mechanism for evaluating them. Use that mechanism when the change requires controlled rollout; do not introduce flag infrastructure or a new switch solely to satisfy this standard. PR size alone does not require a flag.

When a change implements or modifies a feature flag, its rendered PR message names the flag, default state, rollout plan, removal target, and cleanup change. Projects without implemented feature-flag support need neither a flag nor a Feature Flag section.

## Scan

Verify project support from an existing runtime evaluator and its consumers, not a dependency name, PR archetype, or template section. In a project with that support, report a changed flag that is not consumed by its intended behavior or whose PR message omits its operational evidence. Check an ungated change only when the project's rollout requirements call for a flag.

## Fix

Use the project's existing flag implementation and document the changed flag. Do not add a feature-flag system, environment toggle, or kill switch to a project that does not support flags merely to clear a review finding.

```typescript
if (!flags.isEnabled("orders.archive", input.merchantId)) {
  throw new FeatureDisabledError("orders.archive");
}
```

## Edge Cases

- A feature-flag system explicitly requested by the user can establish project support; this standard does not authorize that scope expansion.
- Existing flags unrelated to a change do not require a Feature Flag section.
- Flag retirement removes configuration, telemetry, and tests for both paths.

## Related

GIT-PR-02, GIT-PR-SIZE-01, GIT-PR-SIZE-02, GIT-PR-TYPE-03
