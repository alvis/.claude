# Agent Delegation Map

_Which agent for which trigger, who may spawn whom, and how to fence a spawned subagent_

This is the authoritative map for the 19-agent team introduced by the agent-team overhaul. It is the single
source of truth for delegation routing, spawn topology, and main-session launch suitability. When
`plugins/essential/CLAUDE.md` and this file disagree, this file wins — `CLAUDE.md` links here for the full
picture and only keeps a short summary table.

Each agent is built from `<dir>/base.md` (persona/charter/loop) + `<dir>/frontmatter/claude.json`
(frontmatter as JSON), stitched as `---\n${yaml.dump(JSON.parse(claude.json))}---\n\n${base.md}`.

## (a) Delegation Table — Trigger → Agent

| Trigger | Agent | Role | Why |
| --- | --- | --- | --- |
| Architecture decisions | `raj-patel-techlead` | Tech Lead | Only agent with initiation rights; owns cross-cutting technical direction |
| Complex debugging | `maya-rodriguez-principal` | Principal Engineer | Deep investigation, profiling, root-causing |
| Performance issues | `maya-rodriguez-principal` | Principal Engineer | Optimization and bottleneck elimination |
| Database / data modeling | `ethan-kumar-data-architect` | Data Architect | Schema design, data-entity/data-operation compliance |
| ML / AI features | `zara-ahmad-ml-engineer` | ML Engineer | Model integration, background one-shot runs |
| Deployment automation | `felix-anderson-devops` | DevOps Engineer | CI/CD, infra — background, gated |
| After code implementation | `ava-thompson-testing-evangelist` | Testing Evangelist | Mandatory post-implementation test coverage |
| After security-related changes | `nina-petrov-security-champion` | Security Champion | Mandatory security critique |
| After any code changes | `marcus-williams-code-quality` | Code Quality Critic | Mandatory quality gate, also runs inline as the Marcus-gate Stop hook on gated producers |
| Service / API implementation | `james-mitchell-service-implementation` | Service Implementation Engineer | Owns service/operation build-out, worktree isolation |
| UI / frontend design | `coco-laurent-frontend-designer` | Frontend Designer | Visual/interaction design, worktree isolation |
| DESIGN.md / Notion | `sam-taylor-specification` | Specification Expert | Spec authoring and sync |
| Adversarial / threat-model probing | `kai-raven-adversarial-redteam` | Adversarial Red-Team | Independent attacker-mindset critique, worktree isolation |
| Eval harness / quality gates | `dexter-cho-harness-eval-engineer` | Harness & Eval Engineer | Builds/maintains eval harnesses and gate scaffolding |
| Full lint / type / test sweep | `tess-park-test-runner` | Test Runner | Mechanical, cheap, background, terminal |
| Visual / aesthetic review | `penelope-sterling-aesthetic-evaluator` | Aesthetic Evaluator | Independent aesthetic critique, terminal |
| Project bootstrap | `ada-bishop-initializer` | Project Initializer | Scaffolding new projects, terminal |
| Research / benchmarks / prior art | `nova-chen-research-engineer` | Research Engineer | Literature/benchmark investigation, worktree isolation |
| Data science | `oliver-singh-data-scientist` | Data Scientist | Analysis, experimentation, worktree isolation |
| Workflow / agent-team optimization | `taylor-kim-workflow-optimizer` | Workflow Optimizer | Meta-improvement of agents/skills, background, terminal |

## (b) Spawn-Edge Graph

Edges below are the **intended** spawn edges (`agentEdges`) declared per agent — see binding note (c) for why
these are advisory once a subagent has the `Agent` tool at all.

```
raj-patel-techlead (initiator, main-session only)
  └── * (any registered agent — Raj is the only Agent-Team/Dynamic-Workflow initiator)

maya-rodriguez-principal
  └── marcus-williams-code-quality (critic)
        ├── nina-petrov-security-champion (critic)
        │     └── kai-raven-adversarial-redteam [terminal]
        └── kai-raven-adversarial-redteam [terminal]

james-mitchell-service-implementation
  ├── marcus-williams-code-quality (critic)
  ├── maya-rodriguez-principal
  ├── nina-petrov-security-champion (critic)
  └── tess-park-test-runner [terminal]

ethan-kumar-data-architect
  └── marcus-williams-code-quality (critic)

felix-anderson-devops (background)
  ├── marcus-williams-code-quality (critic)
  ├── nina-petrov-security-champion (critic)
  └── tess-park-test-runner [terminal]

nova-chen-research-engineer
  └── marcus-williams-code-quality (critic)

oliver-singh-data-scientist
  └── marcus-williams-code-quality (critic)

coco-laurent-frontend-designer
  └── penelope-sterling-aesthetic-evaluator [terminal]

dexter-cho-harness-eval-engineer
  └── tess-park-test-runner [terminal]

nina-petrov-security-champion (also reachable directly)
  └── kai-raven-adversarial-redteam [terminal]

Terminal (leaf:true, no Agent tool, cannot spawn):
  ava-thompson-testing-evangelist, zara-ahmad-ml-engineer, taylor-kim-workflow-optimizer,
  sam-taylor-specification, ada-bishop-initializer, penelope-sterling-aesthetic-evaluator,
  kai-raven-adversarial-redteam, tess-park-test-runner
```

8 of the 19 agents are true leaves (`leaf:true`, `Agent` tool omitted from their `tools` list — they cannot
spawn under any circumstance). The remaining 11 have the `Agent` tool and, per the binding note below, can
in practice spawn any registered agent once launched as a subagent — the edges above are the *design intent*,
not a runtime-enforced allowlist.

## (c) Binding Note — Agent(...) Allowlist Scope

The `Agent(agent-name, ...)` parenthetical allowlist in a settings/permission rule **binds on the main
session thread only**. Once an agent is spawned as a subagent and itself holds the `Agent` tool (i.e. it is
not a leaf), that subagent can spawn **any** registered agent — the parenthetical allowlist does not carry
down into subagent contexts. This is a live Claude Code docs behavior, not a spec assumption; the spawn-edge
graph in (b) is therefore advisory design intent for non-leaf agents, and hard enforcement (where required)
must be per-consumer.

To durably fence what a spawned subagent may spawn, ship a `settings.json` `permissions.deny` rule in the
**consumer** repo (this cannot be expressed in agent frontmatter — there is no `permissions` frontmatter
key). Concrete example — prevent any subagent invocation of the adversarial red-team or the tech lead
(e.g. a consumer that wants to keep `kai-raven-adversarial-redteam` and initiation rights main-session-only):

```json
{
  "permissions": {
    "deny": [
      "Agent(kai-raven-adversarial-redteam)",
      "Agent(raj-patel-techlead)"
    ]
  }
}
```

To strip spawn capability from a specific non-leaf agent entirely (belt-and-suspenders on top of its
`tools` list), deny the bare `Agent` tool for that agent's own settings scope:

```json
{
  "permissions": {
    "deny": [
      "Agent"
    ]
  }
}
```

## (d) Felix One-Way-Door Deny Snippet

Felix (`felix-anderson-devops`) runs `mode:auto`, `background:true`, `gated:true` — the classifier
auto-allows reversible operations, but **irreversible, one-way-door operations** (prod deploy, secret
rotation, infra deletion) must never be reachable even under `auto`, and cannot be bound from agent
frontmatter (no `permissions` key exists there). These must be denied at the consumer `settings.json` level:

```json
{
  "permissions": {
    "deny": [
      "Bash(terraform destroy:*)",
      "Bash(terraform apply:*--auto-approve*)",
      "Bash(kubectl delete:*--namespace=prod*)",
      "Bash(kubectl delete:*-n prod*)",
      "Bash(aws secretsmanager rotate-secret:*)",
      "Bash(aws secretsmanager delete-secret:*)",
      "Bash(aws iam:*)",
      "Bash(gcloud secrets versions destroy:*)",
      "Bash(gcloud projects delete:*)",
      "Bash(npm publish:*)",
      "Bash(git push --force*:*main*)",
      "Bash(git push --force*:*master*)",
      "Bash(vercel --prod:*)",
      "Bash(docker push*:prod*)"
    ]
  }
}
```

This is a starting set, not exhaustive — tune the patterns to the consumer's actual deploy/secret/infra
tooling. The principle: anything that cannot be undone by a subsequent agent turn belongs in a deny rule,
never in a permissionMode.

## (e) Topology Map

**Warm core** (trusting team, read each other's context, low-friction handoffs):
`raj-patel-techlead`, `marcus-williams-code-quality`, `ava-thompson-testing-evangelist`,
`james-mitchell-service-implementation`, `dexter-cho-harness-eval-engineer`.

**On-demand specialists** (spun up per task, no standing loop):
`maya-rodriguez-principal`, `ethan-kumar-data-architect`, `nina-petrov-security-champion`,
`nova-chen-research-engineer`, `oliver-singh-data-scientist`, `coco-laurent-frontend-designer`,
`penelope-sterling-aesthetic-evaluator`, `kai-raven-adversarial-redteam`, `sam-taylor-specification`,
`ada-bishop-initializer`.

**Background roles** (externally triggered, one run per spawn, no persistent session):
`felix-anderson-devops`, `zara-ahmad-ml-engineer`, `taylor-kim-workflow-optimizer`.

**Mechanical** (crisp, terse, no persona overhead):
`tess-park-test-runner`.

**Marcus-gate producer loop.** Gated producers (`gated:true`: `maya-rodriguez-principal`,
`ava-thompson-testing-evangelist`, `james-mitchell-service-implementation`,
`ethan-kumar-data-architect`, `felix-anderson-devops`, `zara-ahmad-ml-engineer`,
`dexter-cho-harness-eval-engineer`) embed an inline `type:agent` Stop hook that independently re-reviews
every touched file against deterministic lint/typecheck plus a material-defect review before the producer is
allowed to stop. The review is self-contained (correctness, security, broken contracts, missing tests for new
branches, unhandled errors, convention violations) and additionally applies an in-repo `code-review.md` when
the consumer vendors one — it hardcodes no absolute path, so the gate stays portable when the preset is
bootstrapped into another repo. The hook self-runs the review — gated agents do not need the `Agent` tool for
the gate itself.

- **Convergence predicate**: the hook responds `{"ok": true}` when the touched-file set is empty or passes
  lint/typecheck and the material-defect review clean. Otherwise it responds `{"ok": false, "reason": "..."}`,
  which blocks the Stop and forces another producer turn to address the reason.
- **Iteration cap**: 2 rounds, enforced by a per-agent counter file (`.claude/.gate/<name>-round`) that the
  hook increments each round and honors at `n >= 2`. The counter is the authoritative governor and guarantees
  the gate terminates; `stop_hook_active` is only a fail-safe for the case where that file cannot be read or
  written. At cap the producer is allowed to stop with any remaining issues surfaced in its report for a human
  or a critic (Marcus/Nina/Kai) follow-up rather than looping forever.

## (f) Main-Session Launch-Suitability

Permission mode is set per-agent to match its role; the rationale is uniform: `auto` for reversible-by-default
producers that must never stall unattended, `acceptEdits` for producers whose edits should flow without
per-file prompts (Bash is still checked), `default` for read-mostly critics where interactive prompts are
acceptable because their job is reading and reporting, not mutating.

| Agent | permissionMode | Why launch-safe |
| --- | --- | --- |
| `maya-rodriguez-principal` | auto | fable producer, worktree-isolated, gated — classifier auto-allows reversible investigation/edits, gate catches quality regressions |
| `raj-patel-techlead` | auto | fable orchestrator, only initiator — must never stall waiting for a permission prompt mid-delegation |
| `marcus-williams-code-quality` | default | opus critic, read-mostly — interactive prompts acceptable, edit-prevention rides its critic-fence hook |
| `ava-thompson-testing-evangelist` | acceptEdits | sonnet leaf producer, gated — test-file edits flow, Bash still checked, gate catches broken tests |
| `nina-petrov-security-champion` | default | fable critic, read-mostly — edit-prevention via disallowedTools/fence, prompts acceptable |
| `james-mitchell-service-implementation` | acceptEdits | sonnet producer, worktree-isolated, gated — implementation edits flow freely, gate catches regressions |
| `ethan-kumar-data-architect` | auto | opus producer, gated — schema/data edits are reversible pre-migration, classifier catches risky ops |
| `felix-anderson-devops` | auto | sonnet producer, background, gated — must run unattended; irreversible ops are denied at settings level (see (d)), not relied on for permissionMode |
| `nova-chen-research-engineer` | auto | opus producer, worktree-isolated — research/benchmark work is reversible, no gate needed since it produces reports not shipped code |
| `oliver-singh-data-scientist` | auto | opus producer, worktree-isolated — analysis/experiments are reversible |
| `zara-ahmad-ml-engineer` | auto | opus leaf producer, background, gated — one-shot unattended runs, gate catches quality issues before the run closes |
| `taylor-kim-workflow-optimizer` | auto | opus leaf producer, background — meta-improvement work is reversible (agent/skill file edits, reviewed downstream) |
| `sam-taylor-specification` | acceptEdits | sonnet leaf producer — spec/DESIGN.md edits flow, Bash still checked |
| `ada-bishop-initializer` | acceptEdits | sonnet leaf producer, low effort — scaffolding edits flow, minimal blast radius |
| `coco-laurent-frontend-designer` | auto | fable producer, worktree-isolated — design iteration is reversible, classifier never stalls the loop |
| `penelope-sterling-aesthetic-evaluator` | default | fable leaf critic, read-mostly — interactive prompts acceptable |
| `kai-raven-adversarial-redteam` | default | opus leaf critic, worktree-isolated — read-mostly adversarial probing, sandboxed by its own worktree |
| `dexter-cho-harness-eval-engineer` | auto | opus producer, gated — harness/eval scaffolding is reversible, gate catches quality issues |
| `tess-park-test-runner` | acceptEdits | haiku leaf producer, background — mechanical test-fixture edits flow, cheap and terse |

## (g) Initiation Rights

Only `raj-patel-techlead` may initiate Agent Teams / Dynamic Workflows, and only when running as the **main
session**. No other agent — including warm-core members — has `initiator:true`. A subagent that spawns
further subagents (per the spawn-edge graph in (b)) is still delegating within a single Raj-initiated
workflow, not starting a new one.
