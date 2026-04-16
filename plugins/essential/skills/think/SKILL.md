---
name: think
description: >
  Structured pre-implementation thinking for ambiguous problems.
  Use when there is no crystal-clear instruction or solution on how to solve a
  problem — forces deliberate reasoning before any modification or creation begins.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Bash
argument-hint: [problem-or-question]
---

# Think

Structured deliberate reasoning before acting. Activates whenever a problem lacks a crystal-clear solution path. **You do all thinking yourself — no subagent delegation.**

## Purpose & Scope

**Purpose**: Force explicit reasoning about ambiguous problems before any code, file, or configuration is touched. The output is a decision, not an artifact.

**When to use**:
- The task has multiple valid approaches and it's not obvious which is best
- Requirements are underspecified or contain hidden constraints
- You're about to make an irreversible change and want to validate the approach
- You just left Plan Mode and the plan needs grounding in real constraints

**Hard constraints**:
- NEVER execute, create, or modify files during Steps 1–5
- NEVER delegate to subagents at any point in this skill
- Be opinionated: commit to a recommendation; resolve all "it depends" before presenting

---

## Workflow

`ultrathink`: perform all steps yourself, in sequence.

---

### Step 1: Understand

**What you do**:

1. Parse `$ARGUMENTS`; if empty, surface the ambiguous problem from the conversation context
2. Read up to **3 relevant files** (existing patterns, prior decisions, related skills or standards) to establish real constraints — not imagined ones
3. Write 1–2 sentences answering:
   - What exactly is being asked?
   - Why is it non-trivial? (What makes a naive answer wrong?)
   - What does a bad answer look like?

**Output**: A crisp problem statement anchored in observed constraints.

---

### Step 2: Generate Approaches

**What you do**:

1. Produce **2–3 distinct options** — not variations of the same idea
2. For each option, state explicitly:
   - What it does
   - Cost / complexity
   - Reversibility (can we undo this easily?)
   - What it breaks or ignores
3. Always include a **minimal option**: the smallest possible change that could work
4. **State your recommended option** and the evidence supporting it (from Step 1 observations, not intuition alone)

**Output**: A table or structured list of options with your recommendation clearly marked.

---

### Step 3: Challenge

**What you do**:

1. Write **2–3 strongest objections** to your own recommendation (devil's advocate)
2. For each objection:
   - State whether it changes your recommendation
   - If not, explain specifically why it doesn't (not hand-waving)
3. State: **"What evidence would cause me to switch recommendations?"** — name the specific signal

**Output**: A stress-tested recommendation with explicit falsification criteria.

---

### Step 4: Validate Completeness

Check your recommendation against all of the following. For any item that fails, fix the recommendation before proceeding:

- [ ] No placeholders, "TBD", or deferred decisions
- [ ] All upstream dependencies identified (what must exist or be true first?)
- [ ] At least one edge case or failure mode named
- [ ] Rollback path identified — or explicitly confirmed unnecessary and why

**Output**: A complete, gap-free recommendation.

---

### Step 5: Present & Stop

**What you do**:

Present the recommendation as a clear, opinionated proposal:

```
RECOMMENDATION: [one-sentence summary]

Approach: [chosen option name]
Reasoning: [2-3 sentences — what you observed + why this wins]
Tradeoffs accepted: [what you're giving up]
Edge cases handled: [named]
Rollback: [path or "not needed because X"]

WAITING FOR APPROVAL — not implementing until confirmed.
```

**If the user rejects**: Narrow the specific objection, return to Step 2 with the new constraint.

**If the user approves**: Proceed to Step 6.

---

### Step 6: Handoff

**What you do** (only after explicit approval):

1. Discover available skills:
   ```
   Glob: plugins/*/skills/*/SKILL.md
   ```
2. Read the `name` and `description` frontmatter of the **1–2 most relevant** candidates
3. Select the best-fit skill based on what the approved recommendation requires
4. Invoke that skill with full context: the approved recommendation, observed constraints from Step 1, and any relevant file paths

**Output**: The appropriate skill is invoked with a complete, context-rich prompt.

---

## Examples

### Basic usage

```bash
/think "should we use zod or yup for schema validation"
```

Claude reasons through both options — ecosystem fit, bundle size, existing codebase patterns — commits to a recommendation, stress-tests it, then stops. After approval, discovers and invokes `/coding:write-code` or similar.

### Implicit invocation (no argument)

```bash
/think
```

Claude surfaces the current ambiguous problem from the conversation (e.g., a half-formed request or conflicting requirements) and runs the full reasoning loop on it.

### Architecture decision

```bash
/think "monorepo vs separate repos for our new service"
```

Reads existing repo structure (up to 3 files), generates options with reversibility analysis, challenges its own recommendation, validates completeness, presents with explicit approval gate.
