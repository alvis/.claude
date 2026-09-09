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
```

Use `pending|confirmed|rejected|stale` independently of finding disposition. Add metadata only when it exists: record an answer's source, time, and evidence binding; scope or exceptions when relevant; prior answers when superseded. After a remote check, record `eligible|absent|unverified` with repository, branch, SHA, checked time, evidence, and eligible finding IDs. Retain returned issue URLs for reuse. Omit empty fields; an absent remote check never means eligible.

When no outstanding findings exist, write `No patterns require confirmation.` Preserve prior response history without presenting closed findings as new issue candidates.
