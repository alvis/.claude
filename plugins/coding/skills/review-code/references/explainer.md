# Change explainer

Load this reference only when `--explain` is requested. The review remains
read-only with respect to code; this mode adds one report artifact after the
independent findings are complete.

Generate `<out>/CHANGE_EXPLAINER.md` with these sections:

1. **Outcome and motivation** — the user-visible or system outcome, why the
   change exists, and the acceptance criteria it serves.
2. **Before and after** — distinguish behavior added or changed from relevant
   pre-existing paths the diff relies on. Cite files, symbols, plans, and specs.
3. **Behavior flow** — trace representative entry points through state, data,
   dependencies, side effects, and outputs, including error and async paths.
4. **Decisions and deviations** — summarize implementation notes, accepted
   assumptions, rejected alternatives, plan pivots, and unresolved review
   findings without presenting them as settled facts.
5. **Operational intuition** — invariants, failure modes, security boundaries,
   performance implications, compatibility, and how tests exercise them.
6. **Comprehension quiz** — five to ten questions testing behavior, invariants,
   failure paths, and integration. Avoid trivia recoverable from a filename.
7. **Answer key** — place answers after a clear separator so the reader can take
   the quiz first; each answer cites supporting evidence.

Do not claim the quiz proves correctness or make a perfect score a merge gate.
Its purpose is ownership transfer and reviewer understanding. If evidence is
insufficient for an answer, make that uncertainty an explicit question rather
than inventing certainty.
