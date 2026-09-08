# TYP-TYPE-09: Reuse Shared Contracts

## Intent

Before repeating an inline type, look for an existing shared contract with the same structure and meaning. Reuse it even for a single occurrence; structural assignability alone does not establish the same domain contract.

When an identical inline object type occurs at least twice in one package and no suitable shared contract exists, propose extraction after the complete scan. Two occurrences establish duplication worth a naming decision, not permission to create a type automatically.

## Detection

Run the package analysis described by `coding:skills/lint/SKILL.md` once for the complete selected scope. Count eligible package peers, but report groups only when they touch selected files. Package ownership is the nearest `package.json`, falling back to the repository root; never combine nested packages. Exclude ignored, generated, vendor, dependency, and profile-excluded files.

Compare parsed structure, ignoring formatting and comments while preserving member order, optionality, readonly modifiers, generic bindings, and referenced symbol identity. Named interfaces and aliases are reuse candidates, not inline occurrences. Function types participate in existing-contract reuse; only repeated inline object types trigger extraction proposals. Unresolved symbols require review, not an assertion that two contracts match.

## Fix

```typescript
/** tests whether a value satisfies a condition */
type Predicate<T> = (value: T) => boolean;

interface SelectionOptions<T> {
  accepts: Predicate<T>;
}
```

Reuse `Predicate<Item>` instead of repeating `(value: Item) => boolean` when it is the same contract. Verify generic arguments, domain meaning, accessibility, and import direction; do not create cycles or widen a public surface merely to reuse a name.

<IMPORTANT>
Finish all scan batches before asking about extraction. Present the proposed declaration, owning module, occurrence locations, and affected consumers; offer creation or retaining the inline definitions. Create a shared type only after confirmation, and modify only the authorized scope. Unanswered proposals remain pending. Declined extraction remains a recorded decision, not a confirmed violation or permission to invent another alias.
</IMPORTANT>

Extraction proposals are separate from confirmed violations and lint counters. Repeating an available, semantically matching shared contract is a violation; a proposal without an existing contract is advisory. Confirmed reuse needs no new-type approval. Follow `TYP-TYPE-01` for declaration form after approval: plain object contracts use `interface` except its explicit exceptions.

## Related

TYP-TYPE-01, TYP-PARM-02
