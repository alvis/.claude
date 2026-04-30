# GIT-PR-TYPE-03: Migrations Isolated from Logic

## Severity

error

## Intent

Database schema migrations, data backfills, and config-format upgrades land in dedicated `migration` PRs, never mixed with logic changes. Migration PRs MUST include a `## Rollback` section. Behaviour that depends on the migrated shape lands in a follow-up `implementation` PR, ideally behind a `feature-flag`.

## Fix

```text
order-archive/01-migration   feat(orders-db): [migration] add archived_at column
order-archive/02-flag        feat(orders): [feature-flag] add orders.archive (default off)
order-archive/03-impl        feat(orders): [implementation] use archived_at in archiveOrder
```

Migration PR body:

```markdown
## Category
migration

## Summary
Adds `archived_at TIMESTAMPTZ NULL` to `orders` and an index on `(merchant_id, archived_at)`.

## Rollback
- Drop the new index: `DROP INDEX CONCURRENTLY orders_archived_at_idx;`
- Drop the column: `ALTER TABLE orders DROP COLUMN archived_at;`
- No data loss — column is null for all existing rows
- Rollback is safe at any point because no code reads the column yet (`GIT-PR-TYPE-03`)

## Risk
- Online schema change; uses `CONCURRENTLY` to avoid lock
- Verified on staging clone with production-scale data

## Test plan
- Migration applied and reverted in CI
- Schema diff captured under `migrations/2026-04/`
```

### Why this matters

- A migration that ships with logic changes cannot be rolled back independently.
- Reviewers of a migration look at lock duration, online-safety, and rollback; reviewers of logic look at correctness. Mixing forces both reviews onto every reviewer.
- Splitting migration first, flag second, impl third makes every step independently revertible.

## Edge Cases

- Trivial column-only migrations with literally no consumer change can ship as one PR if the change stays in green zone — but the `## Rollback` section is still required.
- For migrations that cannot be rolled back (data destruction), state explicitly under `## Rollback: NOT REVERSIBLE` and document the forward-only mitigation.
- ORM-driven migrations (Prisma, Drizzle) follow the same rule: the generated SQL plus the schema model are the migration; using the new fields is the implementation.

## Related

GIT-PR-TYPE-01, GIT-PR-TYPE-02, GIT-PR-STACK-04, GIT-PR-SIZE-02
