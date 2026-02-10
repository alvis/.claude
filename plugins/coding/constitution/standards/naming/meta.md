# Naming Standards

_Compact naming rules for functions, types, variables, and data operations._

## Dependent Standards

You MUST also read the following standards together with this file:

- General Coding Principles (standard:universal) - baseline quality and consistency rules
- TypeScript Standards (standard:typescript) - naming must align with type-safety and import rules
- Function Design Standards (standard:function) - function naming must match function design contracts

## What's Stricter Here

This standard enforces requirements beyond typical naming practices:

| Standard Practice                           | Our Stricter Requirement                                               |
|---------------------------------------------|------------------------------------------------------------------------|
| Abbreviations often tolerated               | **Only allowlisted abbreviations are allowed**                         |
| Mixed naming styles across teams            | **One canonical naming model per symbol type**                         |
| `Find*`/`Query*` used loosely               | **Operation verbs are strictly semantic (`Search/List/Get/Set/Drop`)** |
| Prefix-heavy type naming (`IUser`, `TUser`) | **No legacy type prefixes**                                            |

## Exception Policy

Allowed exceptions only when:

- False positive
- No viable workaround exists now

Required exception note fields:

- `rule_id`
- `reason` (`false_positive` or `no_workaround`)
- `evidence`
- `temporary_mitigation`
- `follow_up_action`

If exception note is missing, submission is rejected.

## Rule Groups

- `NAM-CORE-*`: Base naming clarity, casing, abbreviation, and unit precision.
- `NAM-FUNC-*`: Function and operation naming semantics.
- `NAM-TYPE-*`: Type/interface and parameter-contract naming.
- `NAM-DATA-*`: Collection, map, boolean, and iteration naming patterns.
