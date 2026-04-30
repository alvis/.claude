# GIT-PR-TYPE-01: Declare PR Category

## Severity

error

## Intent

Every PR declares exactly one of the 12 PR archetypes — either as a title prefix or as a `## Category` body header. Categorisation drives expected size, required sections, and review depth; an unclassified PR cannot be reviewed against the right checklist.

The 12 categories are: `rfc`, `code-spec`, `contract`, `domain-model`, `implementation`, `integration`, `feature-flag`, `migration`, `ui`, `mechanical-refactor`, `cleanup`, `observability`. See `write.md` -> PR Categories for selection guidance.

## Fix

Title-prefix form (preferred for short, single-category PRs):

```text
feat(orders): [implementation] add archiveOrder operation
refactor(auth): [mechanical-refactor] rename User -> Account via codemod
chore(api-types): [code-spec] add OrderStatus union
```

Body-header form (when the conventional-commit prefix is already saturated):

```markdown
## Category
implementation

## Summary
Adds `archiveOrder()` to the order service.
```

UI PRs include screenshots; migration PRs include rollback; feature-flag PRs name the flag (see related rules).

### Selecting the category

| If the PR is mostly...                        | Use                      |
|-----------------------------------------------|--------------------------|
| A design proposal with no production code     | `rfc`                    |
| Types, interfaces, schemas, JSDoc only        | `code-spec`              |
| External-facing API/wire format               | `contract`               |
| Pure entities/value objects + unit tests      | `domain-model`           |
| Behaviour fulfilling existing types           | `implementation`         |
| Wiring, DI, end-to-end tests                  | `integration`            |
| Adding/flipping/removing a flag               | `feature-flag`           |
| Schema/data migration or backfill             | `migration`              |
| User-facing visual/interaction change         | `ui`                     |
| Renames, file moves, codemods                 | `mechanical-refactor`    |
| Dead-code or deprecation removal              | `cleanup`                |
| Logs, metrics, traces, dashboards             | `observability`          |

## Edge Cases

- A PR that is genuinely two categories (e.g. `migration` + `implementation`) violates `GIT-PR-TYPE-03` and must be split.
- The category prefix is independent of the conventional-commit type (`GIT-MSG-01`); both appear in the title when both are useful.
- For `ui` PRs, the rule is satisfied only when before/after screenshots also appear in the body — categorisation without artefacts is incomplete.

## Related

GIT-MSG-01, GIT-PR-02, GIT-PR-TYPE-02, GIT-PR-TYPE-03, GIT-PR-TYPE-04, GIT-PR-TYPE-05, GIT-PR-STACK-01
