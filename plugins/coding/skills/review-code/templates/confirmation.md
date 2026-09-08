# Pattern confirmation section

Use this section inside the work-root `review.md`, after the derived area roll-up. Repeat the pattern block for distinct shared causes or corrective actions. Link detailed findings rather than copying them. Replace illustrative values; leave `Answer: ` blank until the user responds. The workflow lives in [confirmation.md](directions/confirmation.md).

```markdown
## Pattern confirmation

### PAT-001: <shared problem>

- Findings: <relative area links with stable finding IDs>
- Explanation: <trigger, observed behavior, impact, and proposed correction in plain language>
- Evidence binding: <pattern membership; reviewed SHA/content hashes; supporting source, contract, and test evidence>
- Question: <one short question asking whether the user agrees this shared behavior is an issue>
Answer: 
- Confirmation: pending
- Response provenance: none
- History: none
- Remote eligibility: unchecked
```

Use `pending|confirmed|rejected|stale` for confirmation, independently of finding disposition. A response's provenance names the user, report/chat/generated-prompt source, time, evidence identity, scope, and exceptions. Retain superseded responses with their original bindings in History. Record remote eligibility as `eligible|absent|unverified|unchecked`, with repository, default branch, immutable head SHA, checked time, supporting paths/behavior, and eligible finding IDs when checked. Record any issue URL returned by the issue owner here so a rerun can reuse it.

When no outstanding findings exist, write `No patterns require confirmation.` Preserve prior response history without presenting closed findings as new issue candidates.
